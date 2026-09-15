import os
import json
import urllib.request
import urllib.error

# Priority order:
# 1. SYNAPSE_AI_API_KEY & SYNAPSE_AI_BASE_URL (from .env or local environment)
# 2. HERMES Gateway credentials fallback

def get_api_credentials():
    # 1. Direct Env
    api_key = os.environ.get("SYNAPSE_AI_API_KEY", "")
    base_url = os.environ.get("SYNAPSE_AI_BASE_URL", "")
    model = os.environ.get("SYNAPSE_AI_MODEL", "")

    # 2. Local .env file in SynapseGuild directory
    local_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
    if os.path.exists(local_env):
        with open(local_env, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SYNAPSE_AI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    if val and not api_key: api_key = val
                elif line.startswith("SYNAPSE_AI_BASE_URL="):
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    if val and not base_url: base_url = val
                elif line.startswith("SYNAPSE_AI_MODEL="):
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    if val and not model: model = val

    # 3. Fallback to Hermes system environment
    if not api_key:
        api_key = os.environ.get("HERMES_CUSTOM_OMNI_PEENJEEE_TECH_API_KEY", "")
    if not api_key:
        hermes_env = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(hermes_env):
            with open(hermes_env, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("HERMES_CUSTOM_OMNI_PEENJEEE_TECH_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip().strip("\"'")
                        
    if not base_url:
        base_url = "http://127.0.0.1:20128/v1"
    if not model:
        model = "ag/gemini-3.7-flash-medium"

    return {
        "api_key": api_key,
        "base_url": base_url.rstrip("/"),
        "model": model
    }

def llm_chat(messages, temperature=0.3, max_tokens=2048):
    creds = get_api_credentials()
    api_key = creds["api_key"]
    base_url = creds["base_url"]
    model = creds["model"]
    
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}" if api_key else ""
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw_data = resp.read().decode("utf-8")
            
            # Handle streaming chunks if backend returns event stream
            if raw_data.strip().startswith("data:"):
                text_accum = []
                for line in raw_data.split("\n"):
                    line = line.strip()
                    if line.startswith("data:") and line != "data: [DONE]":
                        chunk_json = line[5:].strip()
                        try:
                            c = json.loads(chunk_json)
                            delta = c.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                text_accum.append(delta)
                        except Exception:
                            pass
                return "".join(text_accum)
            else:
                data = json.loads(raw_data)
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"LLM API Call failed on {url} (Model: {model}): {e}")
