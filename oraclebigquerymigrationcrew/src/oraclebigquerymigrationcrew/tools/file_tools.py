from crewai.tools import tool
from pathlib import Path
import os
from dotenv import load_dotenv
import subprocess
import json

load_dotenv()

DBT_PROJECT_PATH=Path(os.getenv("DBT_PROJECT_PATH"))

@tool()
def write_file(relative_path: str, content: str) -> dict:
    """Write content to a file in the dbt project directory.
    Creates parent directories if they do not exist.
    relative_path is relative to the dbt project root,
    e.g. 'models/staging/stg_orders.sql'
    """
    full_path = DBT_PROJECT_PATH / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return {
        "success": True,
        "path": str(full_path),
        "bytes": len(content)
    }

@tool()
def read_file(relative_path: str) -> str:
    """Read and return the content of a file in the dbt project directory."""
    full_path = DBT_PROJECT_PATH / relative_path
    if not full_path.exists():
        return f"File not found: {relative_path}"
    return full_path.read_text(encoding="utf-8")

@tool()
def commit_to_git(message: str) -> dict:
    """Commit all current changes in the dbt project to the local git repo.
    Stages all files with git add -A then commits with the provided message.
    """
    try:
        subprocess.run(["git", "add", "-A"],
                       cwd=DBT_PROJECT_PATH, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=DBT_PROJECT_PATH, check=True, capture_output=True, text=True
        )
        return {"success": True, "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}
    
@tool()
def push_to_github() -> dict:
    """Push all committed local changes to the remote GitHub repository."""
    try:
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=DBT_PROJECT_PATH, check=True, capture_output=True, text=True
        )
        return {"success": True, "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}
    
@tool()
def read_config() -> dict:
    """Read and return the content of schema_map.json file."""
    full_path = Path("/mnt/c/Users/PALIW/desktop/migration-accelerator-crewai/oraclebigquerymigrationcrew/schema_map.json")
    content =  full_path.read_text(encoding="utf-8")
    return json.loads(content)