# stowify

A lightweight utility to organize dotfiles into a GNU Stow compatible structure.

This script moves files and directories from the user's configured root (e.g., home directory) into a `dotfiles/` style layout for managing with GNU Stow.

Usage

```bash
# Move files from ~/homecopy and scan .config, output to dotfiles
python stowify.py --root ~/homecopy --folders .config --output dotfiles
```

Defaults

- `--root` defaults to `.` (current folder)
- `--folders` defaults to `.config`
- `--output` defaults to `./dotfiles`

License

This project is released under the MIT License — see LICENSE for details.
