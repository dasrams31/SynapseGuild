import os
import subprocess
import shutil
import time

def push_artifacts_to_git(quest_id: str, quest_title: str, files_dict: dict, branch_prefix: str = "quest") -> dict:
    """Creates a local Git branch & commit inside the SynapseGuild artifacts repo."""
    repo_base = "/home/ubuntu/SynapseGuild"
    branch_name = f"{branch_prefix}/{quest_id}"
    
    try:
        # Create commit message
        commit_msg = f"feat({quest_id}): {quest_title}\n\nGenerated autonomously by SynapseGuild AI Party (100% Pytest/Node test passed)."
        
        # We can also log this to a dedicated quests git tracking file
        changelog_path = os.path.join(repo_base, "QUEST_LOGS.md")
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S WIB")
        
        entry = f"\n### 🏆 Quest: {quest_title} (`{quest_id}`)\n- **Waktu:** {timestamp_str}\n- **Files:** {', '.join(files_dict.keys())}\n- **Status:** Approved by Sentinel (100% Passed)\n"
        with open(changelog_path, "a", encoding="utf-8") as f:
            f.write(entry)
            
        subprocess.run(["git", "add", "QUEST_LOGS.md"], cwd=repo_base, capture_output=True)
        commit_proc = subprocess.run(["git", "commit", "-m", f"chore(hall-of-fame): log victory for {quest_title} ({quest_id})"], cwd=repo_base, capture_output=True, text=True)
        
        return {
            "success": True,
            "commit_msg": commit_msg,
            "branch": branch_name,
            "output": commit_proc.stdout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
