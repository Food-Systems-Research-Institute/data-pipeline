from pathlib import Path


def find_project_root(config_name: str = "pyproject.toml", start: Path | None = None) -> Path:
    """Walk up directories until you find config file. 

    Args:
        config_name: Name of config file to find. Defaults to "pyproject.toml"
        start: Path to start walking from. Defaults to None.

    Returns:
        Path: Absolute path to project root
    """
    current_path = (start or Path.cwd()).resolve()
    while current_path != current_path.parent:
        if (current_path / config_name).exists():
            return current_path
        current_path = current_path.parent

    if (current_path / config_name).exists():
        return current_path

    return (start or Path.cwd()).resolve()
