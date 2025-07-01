import glob
import os

import pathspec


def load_gitignore(base_dir: str) -> pathspec.PathSpec:
    """Loads .gitignore patterns from the specified base directory."""
    gitignore_path = os.path.join(base_dir, ".gitignore")
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as f:
            patterns = f.read().splitlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def get_all_project_files(base_dir: str = ".") -> list[str]:
    """Get all files in the project directory recursively."""
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip hidden directories like .git, .venv, etc.
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if not file.startswith("."):  # Skip hidden files
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                all_files.append(rel_path)
    return sorted(all_files)


def filter_paths(paths: list[str], spec: pathspec.PathSpec, base_dir: str = ".") -> list[str]:
    """Filters out paths that match the .gitignore spec and non-text files."""
    filtered_paths = []
    for path in paths:
        normalized_path = os.path.normpath(os.path.join(base_dir, path))
        if not spec.match_file(normalized_path) and os.path.isfile(normalized_path):
            try:
                with open(normalized_path, encoding="utf-8") as f:
                    f.read(1024)
                filtered_paths.append(path)
            except (OSError, UnicodeDecodeError):
                pass
    return filtered_paths


def build_file_tree(paths: list[str], base_dir: str = ".") -> str:
    """Builds an ASCII file tree from a list of paths."""
    tree = {}
    for path in paths:
        parts = path.split(os.sep)
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    def generate_tree_lines(d, prefix=""):
        lines = []
        entries = sorted(d.keys())
        for i, entry in enumerate(entries):
            connector = "├── " if i < len(entries) - 1 else "└── "
            lines.append(prefix + connector + entry)
            if d[entry]:
                extension = "│   " if i < len(entries) - 1 else "    "
                lines.extend(generate_tree_lines(d[entry], prefix + extension))
        return lines

    tree_lines = [base_dir] + generate_tree_lines(tree)
    return "\n".join(tree_lines)


def build_file_blocks(paths: list[str], base_dir: str = ".") -> str:
    """Creates <file="..." /> blocks with the full source code for each file."""
    blocks = []
    for path in paths:
        full_path = os.path.join(base_dir, path)
        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()
                blocks.append(f'<file="{path}">\n{content}\n</file>')
        except (OSError, UnicodeDecodeError) as e:
            blocks.append(f'<file="{path}">\nError reading file: {e}\n</file>')
    return "\n\n".join(blocks)


def build_code_context(file_list: list[str], base_dir: str = ".") -> str:
    """
    Builds the complete code context, including a file tree and file content blocks,
    filtering out ignored and binary files.
    """
    spec = load_gitignore(base_dir)

    # Get complete project tree (like tree --gitignore)
    all_project_files = get_all_project_files(base_dir)
    filtered_all_files = filter_paths(all_project_files, spec, base_dir)
    complete_tree = build_file_tree(filtered_all_files, base_dir)

    # Handle selected files from file_list
    if file_list:
        selected_files = []
        for pattern in file_list:
            selected_files.extend(glob.glob(pattern, recursive=True))

        unique_selected_files = sorted(list(set(selected_files)))
        filtered_selected_files = filter_paths(unique_selected_files, spec, base_dir)

        if filtered_selected_files:
            file_blocks = build_file_blocks(filtered_selected_files, base_dir)
            return f"<file_tree>\n{complete_tree}\n</file_tree>\n\n{file_blocks}"
        else:
            return f"<file_tree>\n{complete_tree}\n</file_tree>\n\nNo files to display from file_list. Check your patterns and .gitignore."
    else:
        # No file_list provided, just show the tree
        return f"<file_tree>\n{complete_tree}\n</file_tree>\n\nNo specific files selected. Use file_list parameter to include file contents."
