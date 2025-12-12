import os
import shutil
import argparse
from pathlib import Path

# --- Configuration ---
# DOTFILES_DIR = Path("dotfiles")
# Files to never move/touch
IGNORE_LIST = open("stowify-ignore").read().strip().split('\n') if os.path.exists("stowify-ignore") else []
# Patterns for stow to ignore (written to .stow-local-ignore)
STOW_IGNORE_PATTERNS = [".DS_Store", ".git", "LICENSE", "README.md"]


def main():
    parser = argparse.ArgumentParser(description="Move files into a stow-compatible structure.")
    parser.add_argument(
        '--root',
        metavar='ROOT',
        type=str,
        default='.',
        help='Root folder the files are currently in. (default: this script\'s folder)'
    )
    parser.add_argument(
        '--folders',
        metavar='FOLDER',
        type=str,
        nargs='*',
        default=['.config'],
        help='List of folders to scan for packages (default: .config)'
    )
    parser.add_argument(
        '--output',
        metavar='OUTPUT',
        type=str,
        default='./dotfiles',
        help='Path to output the stow ready folder to (default: ./dotfiles)'
    )
    args = parser.parse_args()
    root = Path(args.root)
    output = Path(args.output)

    if not root.exists():
        print(f"The root folder doesn't exist: ({root.absolute()})")
        return 1

    # 1. Ensure dotfiles directory exists
    if not output.exists():
        output.mkdir()
        print(f"📁 Created main directory: {output}")

    IGNORE_LIST.append(output.name)
    # 2. Always scan Root Level for dotfiles (e.g. .vimrc)
    scan_root(root, output)

    # 3. Scan user-provided folders (e.g. .config, .local/bin)
    for folder_name in args.folders:
        scan_target_folder(os.path.join(root, folder_name), output)

    # 4. Generate .stow-local-ignore
    create_stow_ignore(output)

    print("\n✨ All operations complete.")


def scan_root(root, output):
    print(f"\n--- 🔍 Scanning Root Level ({root}) ---")

    for item in root.iterdir():
        if item.name in IGNORE_LIST:
            continue

        # Logic: Only move files starting with '.' in the root
        if item.is_file() and item.name.startswith("."):
            pkg_name = item.name.lstrip(".")  # .vimrc -> vimrc

            # Destination: dotfiles/vimrc/.vimrc
            dest_dir = output / pkg_name
            dest_path = dest_dir / item.name

            move_item(item, dest_dir, dest_path)


def scan_target_folder(folder, output):
    target_path = Path(folder)

    if not target_path.exists():
        print(f"⚠️  Skipping '{folder}': Path not found.")
        return

    print(f"\n--- 🔍 Scanning {folder} ---")

    # Iterate over items INSIDE the target folder
    for item in target_path.iterdir():
        if item.name in IGNORE_LIST:
            continue

        # Logic: The item name becomes the package name
        pkg_name = item.name

        # We need to recreate the full relative path inside the package
        # Example: .local/bin/script -> dotfiles/script/.local/bin/script

        # relative_parent is ".local/bin"
        relative_parent = item.parent.name

        dest_dir = output / pkg_name / relative_parent
        dest_path = dest_dir / item.name

        move_item(item, dest_dir, dest_path)


def move_item(source, dest_parent, dest_final):
    """
    Moves source to dest_final, creating parents as needed.
    """
    pkg_name = dest_final.parts[1]  # dotfiles/{pkg_name}/...
    print(f"📦 Packaging: {source}")
    print(f"   -> Package: {pkg_name}")
    print(f"   -> Path:    {dest_final}")

    if dest_final.exists():
        print(f"   ❌ Error: Destination already exists ({dest_final})")
        return

    # Create the directory structure
    dest_parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(source), str(dest_final))
        print("   ✅ Moved")
    except Exception as e:
        print(f"   ❌ Error moving file: {e}")


def create_stow_ignore(output):
    """
    Creates a .stow-local-ignore file to prevent Stow from
    symlinking git files or OS junk.
    """
    ignore_file = output / ".stow-local-ignore"
    if not ignore_file.exists():
        with open(ignore_file, "w") as f:
            for pattern in STOW_IGNORE_PATTERNS:
                f.write(f"{pattern}\n")
        print(f"\n🛡️  Generated {ignore_file} to ignore git/system files.")


if __name__ == "__main__":
    main()
