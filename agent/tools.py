import pathlib
from langchain_core.tools import tool

PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"


def safe_path_for_project(path: str) -> pathlib.Path:
    base = PROJECT_ROOT.resolve()
    p = (base / path).resolve()

    if not str(p).startswith(str(base)):
        raise ValueError("Attempt to write outside project root")

    return p


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file inside the project root."""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

    return f"WROTE:{p}"


@tool
def read_file(path: str) -> str:
    """Read content from a file inside the project root."""
    p = safe_path_for_project(path)

    if not p.exists():
        return f"ERROR: File does not exist: {p}"

    with open(p, "r", encoding="utf-8") as f:
        return f.read()


@tool
def list_files(directory: str = ".") -> str:
    """List all files inside the project root directory."""
    p = safe_path_for_project(directory)

    if not p.is_dir():
        return f"ERROR: {p} is not a directory"

    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
    return "\n".join(files) if files else "No files found."


@tool
def get_current_directory() -> str:
    """Return the current project root directory."""
    return str(PROJECT_ROOT)


def init_project_root():
    """Initialize the project root directory."""
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)
