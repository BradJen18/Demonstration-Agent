from fnmatch import fnmatch
from datetime import datetime
from pathlib import Path
import requests
import os
from langchain.tools import tool


# Files outside this directory can never be accessed by the agent.
SAFE_ROOT = Path(__file__).resolve().parent

# Names the agent may not read or see, matched against every path component.
SENSITIVE_PATTERNS = [".env", ".env.*","main.py"]

def _is_allowed(resolved: Path) -> bool:
    """Whether a resolved path is inside SAFE_ROOT and not sensitive."""
    if not resolved.is_relative_to(SAFE_ROOT):
        return False
    return not any(
        fnmatch(part, pattern)
        for part in resolved.relative_to(SAFE_ROOT).parts
        for pattern in SENSITIVE_PATTERNS
    )


def _resolve_safe(path: str) -> Path:
    # resolve() collapses ".." and follows symlinks, so the check below
    # sees the real location.
    target = (SAFE_ROOT / path).resolve()

    # Use one generic error for every case so we don't leak which paths exist.
    if not _is_allowed(target):
        raise PermissionError("Access denied or file not found.")

    return target


def read_safe_file(path: str) -> str:
    """Read a UTF-8 text file from the project directory.

    Args:
        path: File path relative to the project root, e.g. "docs/readme.txt".
    """
    target = _resolve_safe(path)
    if not target.is_file():
        raise PermissionError("Access denied or file not found.")

    return target.read_text(encoding="utf-8")


def list_directory(path: str = ".") -> str:
    """List the contents of a directory in the project. Subdirectories end with "/".

    Args:
        path: Directory path relative to the project root. Defaults to the root.
    """
    target = _resolve_safe(path)
    if not target.is_dir():
        raise PermissionError("Access denied or directory not found.")

    entries = sorted(
        entry.name + "/" if entry.is_dir() else entry.name
        for entry in target.iterdir()
        if _is_allowed(entry.resolve())
    )
    return "\n".join(entries) or "(empty directory)"

@tool
def write_safe_file(path: str, content: str) -> str:
    """Write text content to a file in the project directory.

    Args:
        path: File path relative to the project root.
        content: The text content to write.
    """
    target = _resolve_safe(path)
    # Add any extra safety checks you need here
    target.write_text(content, encoding="utf-8")
    return f"Successfully wrote to {path}"

@tool
def get_weather(lat:str,lon:str) -> str:
    """find the longitude and latitude for location stated and give the weather for that location"""

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("Can't find API key")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "units": "imperial","appid":api_key}

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def add_memory(entry: str, log_path: str = "memory.log"):
    """Add relevant information to your long term memonry for later access."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_entry = f"- **[{timestamp}]**: {entry}\n"
    
    path = Path(log_path)
    if not path.exists():
        path.write_text("# Learning Memory Log\n\n## Entries\n", encoding="utf-8")
        
    with open(path, "a", encoding="utf-8") as f:
        f.write(formatted_entry)
    print(f"Memory recorded: {entry}")

