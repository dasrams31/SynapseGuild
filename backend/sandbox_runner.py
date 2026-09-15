import os
import subprocess
import shutil
import time
import sys

SANDBOX_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sandbox"))
os.makedirs(SANDBOX_BASE_DIR, exist_ok=True)

# Python runner venv
SYNAPSE_VENV_PYTHON = "/home/ubuntu/SynapseGuild/venv/bin/python"
PYTHON_EXEC = SYNAPSE_VENV_PYTHON if os.path.exists(SYNAPSE_VENV_PYTHON) else sys.executable

class CodeSandbox:
    def __init__(self, quest_id: str, language: str = "python"):
        self.quest_id = quest_id
        self.language = language.lower() # python | nodejs
        self.quest_dir = os.path.join(SANDBOX_BASE_DIR, quest_id)
        os.makedirs(self.quest_dir, exist_ok=True)

    def write_file(self, rel_path: str, content: str) -> str:
        full_path = os.path.join(self.quest_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return full_path

    def read_file(self, rel_path: str) -> str:
        full_path = os.path.join(self.quest_dir, rel_path)
        if not os.path.exists(full_path):
            return ""
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_files(self) -> list:
        file_list = []
        for root, _, files in os.walk(self.quest_dir):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), self.quest_dir)
                file_list.append(rel)
        return file_list

    def run_tests(self) -> dict:
        """Runs language-specific test runners (pytest for Python, node --test for JavaScript/TypeScript)."""
        start_time = time.time()
        
        if self.language in ["javascript", "typescript", "nodejs", "node"]:
            # Native Node.js test runner (Node >= 18 has built-in node --test)
            cmd = ["node", "--test"]
        else:
            # Default Python pytest runner
            cmd = [PYTHON_EXEC, "-m", "pytest", "-v", "--tb=short"]
            
        try:
            res = subprocess.run(
                cmd,
                cwd=self.quest_dir,
                capture_output=True,
                text=True,
                timeout=25
            )
            duration = time.time() - start_time
            return {
                "passed": res.returncode == 0,
                "return_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_seconds": round(duration, 3),
                "runner": "node:test" if "node" in self.language else "pytest"
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "return_code": -1,
                "stdout": "",
                "stderr": "Execution timed out (Limit 25s exceeded in sandbox)",
                "duration_seconds": 25.0,
                "runner": self.language
            }
        except Exception as e:
            return {
                "passed": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Runner failure: {str(e)}",
                "duration_seconds": 0.0,
                "runner": self.language
            }

    def wipe(self):
        if os.path.exists(self.quest_dir):
            shutil.rmtree(self.quest_dir, ignore_errors=True)
