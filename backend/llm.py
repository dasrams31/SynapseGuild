import os
import json
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.hermes/.env")

def get_api_credentials():
    api_key = os.environ.get("HERMES_CUSTOM_OMNI_PEENJEEE_TECH_API_KEY", "")
    if not api_key and os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            for line in f:
                if line.strip().startswith("HERMES_CUSTOM_OMNI_PEENJEEE_TECH_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip().strip("\"'")
    return api_key

def llm_chat(messages, model="ag/gemini-3.7-flash-medium", temperature=0.3, max_tokens=2048):
    api_key = get_api_credentials()
    url = "http://127.0.0.1:20128/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
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
            
            # Handle SSE chunks if router returns data stream format
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
        raise RuntimeError(f"LLM API Call failed: {e}")
