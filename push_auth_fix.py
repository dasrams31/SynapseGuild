import os
import subprocess

token_file = "/home/ubuntu/SynapseGuild/.gitlab_token"
if not os.path.exists(token_file):
    with open(token_file, "w") as f:
        f.write("glpat-rkekHDtXeexQbWPqoiBsmGM6MQpvOjEKdTpubmV1NA8.01.170u0m8r2")

with open(token_file, "r") as f:
    token = f.read().strip()

repo_dir = "/home/ubuntu/SynapseGuild"
remote_url = f"https://oauth2:{token}@gitlab.com/RamsNotes31/synapseguild-rpg-agent.git"

subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
subprocess.run(["git", "commit", "-m", "fix(auth): configure default admin credentials (dasrams) and push stable SQLite auth system to GitLab"], cwd=repo_dir, check=True)

subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=repo_dir, check=True)
proc = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_dir, capture_output=True, text=True)
print("Push Result:\n", proc.stdout)
if proc.stderr:
    print("Push Stderr:\n", proc.stderr.replace(token, "[REDACTED]"))

subprocess.run(["git", "remote", "set-url", "origin", "https://gitlab.com/RamsNotes31/synapseguild-rpg-agent.git"], cwd=repo_dir, check=True)
os.remove(token_file)
