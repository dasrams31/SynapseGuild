import os
import subprocess
import shutil
import time
import sys

SANDBOX_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sandbox"))
os.makedirs(SANDBOX_BASE_DIR, exist_ok=True)

# Use current python executable or venv python
PYTHON_EXEC = sys.executable

class CodeSandbox:
    def __init__(self, quest_id: str):
        self.quest_id = quest_id
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
        """Runs pytest or python -m unittest inside the isolated quest directory."""
        cmd = [PYTHON_EXEC, "-m", "pytest", "-v", "--tb=short"]
        start_time = time.time()
        try:
            res = subprocess.run(
                cmd,
                cwd=self.quest_dir,
                capture_output=True,
                text=True,
                timeout=25
            )
            duration = round(time.time() - start_time, 2)
            passed = (res.returncode == 0)
            
            # Fallback to unittest if pytest collected 0 items
            if not passed and "collected 0 items" in res.stdout:
                res_u = subprocess.run(
                    [PYTHON_EXEC, "-m", "unittest", "discover"],
                    cwd=self.quest_dir,
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                passed = (res_u.returncode == 0)
                res.stdout += "\n" + res_u.stdout
                res.stderr += "\n" + res_u.stderr

            score = 100 if passed else max(0, 70 - (res.stdout.count("FAILED") * 20))
            
            return {
                "passed": passed,
                "score": score,
                "duration_seconds": duration,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "return_code": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "score": 0,
                "duration_seconds": 25.0,
                "stdout": "",
                "stderr": "Test execution timed out",
                "return_code": -1
            }
        except Exception as e:
            return {
                "passed": False,
                "score": 0,
                "duration_seconds": 0.0,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

    def cleanup(self):
        if os.path.exists(self.quest_dir):
            shutil.rmtree(self.quest_dir, ignore_errors=True)
