from utils import find_project_root


def add(x, y):
    return x + y


def test_add_adds_properly():
    assert add(1, 2) == 3


def test_find_project_root_finds_root_from_root(tmp_path):
    (tmp_path / "pyproject.toml").write_text("this is pyproject.toml")

    root = find_project_root("pyproject.toml", tmp_path)
    assert root == tmp_path


def test_find_project_root_finds_root_from_nested_dir(tmp_path):
    (tmp_path / "pyproject.toml").write_text("this is pyproject.toml")

    dir_path = tmp_path / "other_dir"
    dir_path.mkdir()

    root = find_project_root("pyproject.toml", dir_path)

    assert root == tmp_path
