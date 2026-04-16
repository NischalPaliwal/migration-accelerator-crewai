import os
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List
from filelock import FileLock
from crewai.tools import tool

LOG_PATH = Path("/mnt/c/Users/PALIW/desktop/migration-accelerator-crewai/oraclebigquerymigrationcrew/state/migration_log.json")
LOCK_PATH = LOG_PATH.with_suffix(".json.lock")

@tool()
def write_migration_log(
    object_name: str,
    status: str,
    raw_source: str,
    object_type: Optional[str] = None,
    schema: Optional[str] = None,
    depends_on: Optional[List[str]] = None,
    row_count: Optional[int] = None,
    complexity: Optional[str] = None,
    migration_strategy: Optional[str] = None,
    migration_order_index: Optional[int] = None,
    blocked_until: Optional[List[str]] = None,
    failure_reason: Optional[str] = None,
) -> str:
    """Write or update an object's entry in the migration log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(LOCK_PATH, timeout=10)

    with lock:
        log = {}
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 0:
            try:
                log = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                log = {}

        key = object_name.upper()
        log[key] = {
            **(log.get(key, {})),
            "object_name":           object_name,
            "status":                status.upper(),
            "object_type":           object_type,
            "raw_source":            raw_source,
            "schema":                schema,
            "complexity":            complexity,
            "migration_strategy":    migration_strategy,
            "depends_on":            depends_on or [],
            "row_count":             row_count,
            "failure_reason":        failure_reason,
            "migration_order_index": migration_order_index,
            "blocked_until":         blocked_until or [],
            "last_updated":          datetime.now(timezone.utc).isoformat(),
        }

        fd, temp_path = tempfile.mkstemp(dir=LOG_PATH.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                json.dump(log, tmp, indent=2)
            os.replace(temp_path, LOG_PATH)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return json.dumps({"success": False, "error": str(e)})

    return json.dumps({"success": True, "object_name": object_name, "status": status})


@tool()
def read_migration_log(object_name: str) -> str:
    """Read an object's entry in the migration log."""
    if not LOG_PATH.exists():
        return json.dumps({"found": False, "object_name": object_name, "reason": "Log file does not exist"})

    lock = FileLock(LOCK_PATH, timeout=5)
    with lock:
        try:
            log = json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return json.dumps({"found": False, "error": "Log file is corrupted"})

    key = object_name.upper()
    if key not in log:
        return json.dumps({"found": False, "object_name": object_name, "reason": "No log entry found"})

    return json.dumps({**log[key], "found": True})