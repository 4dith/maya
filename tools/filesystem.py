import shutil
import subprocess
from pathlib import Path
PROJECT_ROOT = Path.cwd().resolve()

IGNORED_DIRS = {
    ".git",
    ".idea",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".wwebjs_auth",
    ".wwebjs_cache",
}

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
}

def resolve_path(relative_path: str) -> Path:
    """Resolve a path and ensure it stays inside the project."""
    candidate = Path(relative_path)

    if candidate.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    resolved = (PROJECT_ROOT / candidate).resolve(strict=True)

    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError("Path is outside the project.")

    if any(part in SENSITIVE_NAMES for part in resolved.parts):
        raise ValueError("Access to sensitive files is denied.")

    return resolved


def list_files(directory: str = ".") -> dict:
    """List files in the project, excluding common generated directories."""
    root = resolve_path(directory)

    if not root.is_dir():
        raise ValueError("Path must be a directory.")

    results = []

    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        # Avoid traversing symlinks.
        if path.is_symlink():
            continue

        if not path.is_file():
            continue

        if path.name in SENSITIVE_NAMES:
            continue

        results.append(str(path.relative_to(PROJECT_ROOT)))

        if len(results) >= 500:
            break

    return {"files": results}


def read_file(path: str) -> dict:
    """Read a UTF-8 text file from the project."""
    file_path = resolve_path(path)

    if not file_path.is_file():
        raise ValueError("Not a file.")

    if file_path.stat().st_size > 100_000:
        raise ValueError("File exceeds the 100 KB limit.")

    content = file_path.read_bytes()

    if b"\x00" in content:
        raise ValueError("Binary files are not supported.")

    return {
        "path": str(file_path.relative_to(PROJECT_ROOT)),
        "content": content.decode("utf-8"),
    }


def edit_file(path: str, old_text: str, new_text: str) -> dict:
    """Replace an exact, unique piece of text and save the file."""
    try:
        file_path = resolve_path(path)

        if not file_path.is_file():
            return {"error": "Not a file."}

        if file_path.stat().st_size > 100_000:
            return {"error": "File exceeds the 100 KB limit."}

        content = file_path.read_text(encoding="utf-8")

        if not old_text:
            return {"error": "old_text cannot be empty."}

        occurrences = content.count(old_text)

        if occurrences == 0:
            return {"error": "The specified text was not found."}

        if occurrences > 1:
            return {
                "error": (
                    f"The specified text occurs {occurrences} times. "
                    "Provide a more specific section."
                )
            }

        updated_content = content.replace(old_text, new_text, 1)
        file_path.write_text(updated_content, encoding="utf-8")

        return {
            "status": "success",
            "path": str(file_path.relative_to(PROJECT_ROOT)),
            "message": "File edited successfully.",
        }

    except (ValueError, UnicodeDecodeError, OSError) as exc:
        return {"error": str(exc)}


def write_file(path: str, content: str) -> dict:
    """Create a file or overwrite an existing project file."""
    try:
        file_path = resolve_path(path) if (PROJECT_ROOT / path).exists() else (
            PROJECT_ROOT / path
        ).resolve()

        if not file_path.is_relative_to(PROJECT_ROOT):
            return {"error": "Path is outside the project."}

        if any(part in SENSITIVE_NAMES for part in file_path.parts):
            return {"error": "Access to sensitive files is denied."}

        if file_path.is_symlink():
            return {"error": "Writing through symlinks is not allowed."}

        if file_path.exists() and not file_path.is_file():
            return {"error": "Path exists but is not a file."}

        if len(content.encode("utf-8")) > 100_000:
            return {"error": "Content exceeds the 100 KB limit."}

        # Require the parent directory to exist.
        if not file_path.parent.is_dir():
            return {"error": "Parent directory does not exist."}

        file_path.write_text(content, encoding="utf-8")

        return {
            "status": "success",
            "path": str(file_path.relative_to(PROJECT_ROOT)),
            "message": "File written successfully.",
        }

    except (ValueError, UnicodeDecodeError, OSError) as exc:
        return {"error": str(exc)}


def move_file(source: str, destination: str) -> dict:
    """Move or rename a file within the project."""
    try:
        src = resolve_path(source)
        dst = (PROJECT_ROOT / destination).resolve()

        if not dst.is_relative_to(PROJECT_ROOT):
            return {"error": "Destination is outside the project."}

        if src.is_symlink() or dst.is_symlink():
            return {"error": "Moving symlinks is not allowed."}

        if not src.is_file():
            return {"error": "Source must be an existing file."}

        if any(part in IGNORED_DIRS for part in src.relative_to(PROJECT_ROOT).parts):
            return {"error": "Source is in an ignored directory."}

        if any(part in IGNORED_DIRS for part in dst.relative_to(PROJECT_ROOT).parts):
            return {"error": "Destination is in an ignored directory."}

        if any(part in SENSITIVE_NAMES for part in dst.relative_to(PROJECT_ROOT).parts):
            return {"error": "Destination is a sensitive path."}

        if dst.exists():
            return {"error": "Destination already exists."}

        if not dst.parent.is_dir():
            return {"error": "Destination directory does not exist."}

        shutil.move(str(src), str(dst))

        return {
            "status": "success",
            "source": str(src.relative_to(PROJECT_ROOT)),
            "destination": str(dst.relative_to(PROJECT_ROOT)),
        }

    except (ValueError, OSError) as exc:
        return {"error": str(exc)}


def copy_file(source: str, destination: str) -> dict:
    """Copy a file to another location within the project."""
    try:
        src = resolve_path(source)
        dst = (PROJECT_ROOT / destination).resolve()

        if not dst.is_relative_to(PROJECT_ROOT):
            return {"error": "Destination is outside the project."}

        if src.is_symlink() or dst.is_symlink():
            return {"error": "Copying symlinks is not allowed."}

        if not src.is_file():
            return {"error": "Source must be an existing file."}

        if any(part in IGNORED_DIRS for part in src.relative_to(PROJECT_ROOT).parts):
            return {"error": "Source is in an ignored directory."}

        if any(part in IGNORED_DIRS for part in dst.relative_to(PROJECT_ROOT).parts):
            return {"error": "Destination is in an ignored directory."}

        if any(part in SENSITIVE_NAMES for part in src.relative_to(PROJECT_ROOT).parts):
            return {"error": "Copying sensitive files is not allowed."}

        if any(part in SENSITIVE_NAMES for part in dst.relative_to(PROJECT_ROOT).parts):
            return {"error": "Destination is a sensitive path."}

        if dst.exists():
            return {"error": "Destination already exists."}

        if not dst.parent.is_dir():
            return {"error": "Destination directory does not exist."}

        shutil.copy2(src, dst)

        return {
            "status": "success",
            "source": str(src.relative_to(PROJECT_ROOT)),
            "destination": str(dst.relative_to(PROJECT_ROOT)),
        }

    except (ValueError, OSError) as exc:
        return {"error": str(exc)}


def delete_file(path: str) -> dict:
    """Delete a file within the project."""
    try:
        file_path = resolve_path(path)

        if file_path.is_symlink():
            return {"error": "Deleting symlinks is not allowed."}

        if not file_path.is_file():
            return {"error": "Path must be an existing file."}

        relative_path = file_path.relative_to(PROJECT_ROOT)

        if any(part in IGNORED_DIRS for part in relative_path.parts):
            return {"error": "Deleting files in ignored directories is not allowed."}

        file_path.unlink()

        return {
            "status": "success",
            "path": str(relative_path),
            "message": "File deleted successfully.",
        }

    except (ValueError, OSError) as exc:
        return {"error": str(exc)}


def git_diff(staged: bool = False) -> dict:
    """Show Git changes in the project."""
    try:
        command = ["git", "diff", "--no-ext-diff", "--unified=3"]

        if staged:
            command.append("--cached")

        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode != 0:
            return {
                "error": result.stderr.strip() or "Git diff failed."
            }

        return {
            "status": "success",
            "staged": staged,
            "diff": result.stdout or "No changes found.",
        }

    except subprocess.TimeoutExpired:
        return {"error": "Git diff timed out."}
    except OSError as exc:
        return {"error": str(exc)}
