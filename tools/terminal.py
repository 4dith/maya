
# tools/terminal.py

import subprocess

from tools.filesystem import PROJECT_ROOT


def run_command(command: str, timeout: int = 30) -> dict:
    """Run a terminal command in the project directory."""

    if not command.strip():
        return {"error": "Command cannot be empty."}

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )

        return {
            "command": command,
            "stdout": result.stdout[-15000:],
            "stderr": result.stderr[-15000:],
            "returncode": result.returncode,
            "success": result.returncode == 0,
        }

    except subprocess.TimeoutExpired:
        return {
            "error": f"Command timed out after {timeout} seconds."
        }

    except OSError as exc:
        return {"error": str(exc)}
