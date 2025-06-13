import os
import tempfile

import pytest

from phone_a_friend_mcp_server.utils.context_builder import (
    build_code_context,
    build_file_blocks,
    build_file_tree,
    filter_paths,
    load_gitignore,
)


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create .gitignore
        with open(os.path.join(temp_dir, ".gitignore"), "w") as f:
            f.write("*.pyc\n")
            f.write("__pycache__/\n")
            f.write("*.log\n")
            f.write("dist/\n")

        # Create some files and directories
        os.makedirs(os.path.join(temp_dir, "src", "__pycache__"))
        with open(os.path.join(temp_dir, "src", "main.py"), "w") as f:
            f.write("print('hello')\n")
        with open(os.path.join(temp_dir, "src", "main.pyc"), "w") as f:
            f.write("binary_content")
        with open(os.path.join(temp_dir, "src", "__pycache__", "cache.pyc"), "w") as f:
            f.write("cached_binary")
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Project\n")
        os.makedirs(os.path.join(temp_dir, "dist"))
        with open(os.path.join(temp_dir, "dist", "package.tar.gz"), "w") as f:
            f.write("package_content")
        with open(os.path.join(temp_dir, "app.log"), "w") as f:
            f.write("log message")

        yield temp_dir


def test_load_gitignore(temp_project):
    spec = load_gitignore(temp_project)
    assert spec.match_file(os.path.join(temp_project, "src/main.pyc"))
    assert spec.match_file(os.path.join(temp_project, "dist/somefile"))
    assert not spec.match_file(os.path.join(temp_project, "src/main.py"))


def test_filter_paths(temp_project):
    spec = load_gitignore(temp_project)
    all_paths = ["src/main.py", "src/main.pyc", "README.md", "dist/package.tar.gz", "app.log"]
    filtered = filter_paths(all_paths, spec, temp_project)
    assert "src/main.py" in filtered
    assert "README.md" in filtered
    assert "src/main.pyc" not in filtered
    assert "dist/package.tar.gz" not in filtered
    assert "app.log" not in filtered


def test_build_file_tree():
    paths = ["src/main.py", "src/utils/helpers.py", "README.md"]
    tree = build_file_tree(paths, base_dir=".")
    expected_tree = """
.
├── README.md
└── src
    ├── main.py
    └── utils
        └── helpers.py
""".strip()
    assert tree.strip() == expected_tree


def test_build_file_blocks(temp_project):
    paths = ["src/main.py", "README.md"]
    blocks = build_file_blocks(paths, temp_project)
    assert '<file="src/main.py">' in blocks
    assert "print('hello')" in blocks
    assert '<file="README.md">' in blocks
    assert "# Project" in blocks


def test_build_code_context(temp_project):
    file_list = ["src/main.py", "src/main.pyc", "README.md", "dist/package.tar.gz", "app.log"]
    # Change CWD to temp_project for glob to work correctly
    original_cwd = os.getcwd()
    os.chdir(temp_project)
    try:
        context = build_code_context(file_list, base_dir=".")
    finally:
        os.chdir(original_cwd)

    assert "<file_tree>" in context
    assert "main.py" in context
    assert "README.md" in context
    assert "main.pyc" not in context
    assert "dist" not in context
    assert "app.log" not in context
    assert '<file="src/main.py">' in context
    assert "print('hello')" in context
    assert '<file="README.md">' in context
    assert "# Project" in context
