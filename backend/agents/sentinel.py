from llm import llm_chat
import json

SENTINEL_SYSTEM_PROMPT = """You are THE SENTINEL (The Grand Inquisitor / Zero-Trust Code Auditor) in SynapseGuild.
Your role:
1. Audit the source code, review pytest output from the sandbox execution, and evaluate against acceptance criteria.
2. Determine if the quest has been successfully completed or requires rework.

Output MUST be valid JSON strictly matching this schema:
{
  "dialogue": "Short in-character speech for the RPG speech bubble (max 2 sentences)",
  "approved": true, // boolean (true if all tests pass and code is safe/accurate)
  "score": 95, // integer 0-100
  "review_summary": "Concise summary of findings, strengths, or defects"
}
"""

def run_sentinel(spec: str, test_criteria: str, files: dict, sandbox_result: dict) -> dict:
    user_content = (
        f"Specs:\n{spec}\n\n"
        f"Acceptance Criteria:\n{test_criteria}\n\n"
        f"Generated Files:\n{json.dumps(files, indent=2)}\n\n"
        f"Real Sandbox Pytest Results:\n"
        f"Passed: {sandbox_result.get('passed')}\n"
        f"Exit Code: {sandbox_result.get('return_code')}\n"
        f"Stdout:\n{sandbox_result.get('stdout')}\n"
        f"Stderr:\n{sandbox_result.get('stderr')}"
    )

    messages = [
        {"role": "system", "content": SENTINEL_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    
    raw = llm_chat(messages, temperature=0.1)
    clean = raw.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()
    
    try:
        data = json.loads(clean)
        # Sandbox pytest is authoritative: if pytest returned non-zero, approval MUST be False
        if not sandbox_result.get("passed", False):
            data["approved"] = False
            data["score"] = min(data.get("score", 50), 65)
        return data
    except Exception:
        passed = sandbox_result.get("passed", False)
        return {
            "dialogue": "Semua pengujian lolos sempurna di Altar!" if passed else "Pengujian gagal! Rombak kembali kodenya di Forge!",
            "approved": passed,
            "score": 100 if passed else 50,
            "review_summary": raw
        }
