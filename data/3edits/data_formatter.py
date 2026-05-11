"""
Reorganizes image tuples from nested setting folders into flat data folders.

Input structure:
  root/
    setting_1/
      subfolder_A/
        a.png, a_prime.png, b.png, b_prime.png
      subfolder_B/
        a.png, a_prime.png, b.png, b_prime.png
    setting_2/
      ...

Output structure:
  root/
    data1/
      a.png, a_prime.png, b.png, b_prime.png
    data2/
      a.png, a_prime.png, b.png, b_prime.png
    ...
"""

import os
import shutil
import re
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
ROOT = Path(".")          # Change to your root directory path if needed
REQUIRED_FILES = {"a.png", "a_prime.png", "b.png", "b_prime.png"}
DRY_RUN = False           # Set to True to preview actions without copying files
# ──────────────────────────────────────────────────────────────────────────────


def find_setting_folders(root: Path) -> list[Path]:
    """Return all folders matching setting_<number> pattern, sorted numerically."""
    pattern = re.compile(r"^setting(\d+)$", re.IGNORECASE)
    folders = []
    for entry in root.iterdir():
        if entry.is_dir() and pattern.match(entry.name):
            folders.append(entry)
    folders.sort(key=lambda p: int(pattern.match(p.name).group(1)))
    return folders


def find_image_tuples(setting_folder: Path) -> list[Path]:
    """Return all subfolders that contain the full set of required images."""
    tuples = []
    for subfolder in sorted(setting_folder.iterdir()):
        if not subfolder.is_dir():
            continue
        present = {f.name for f in subfolder.iterdir() if f.is_file()}
        if REQUIRED_FILES.issubset(present):
            tuples.append(subfolder)
        else:
            missing = REQUIRED_FILES - present
            print(
                f"  [SKIP] {subfolder} — missing: {', '.join(sorted(missing))}")
    return tuples


def main():
    root = ROOT.resolve()
    print(f"Root directory : {root}")
    print(f"Dry run        : {DRY_RUN}\n")

    setting_folders = find_setting_folders(root)
    if not setting_folders:
        print("No setting_# folders found. Exiting.")
        return

    print(f"Found {len(setting_folders)} setting folder(s): "
          f"{[f.name for f in setting_folders]}\n")

    data_counter = 1

    for setting in setting_folders:
        print(f"Processing {setting.name}/")
        image_tuples = find_image_tuples(setting)

        for src_folder in image_tuples:
            dest_folder = root / f"data{data_counter}"

            print(f"  {src_folder.relative_to(root)}  →  {dest_folder.name}/")

            if not DRY_RUN:
                dest_folder.mkdir(exist_ok=True)
                for filename in REQUIRED_FILES:
                    shutil.copy2(src_folder / filename, dest_folder / filename)

            data_counter += 1

        print()

    total = data_counter - 1
    action = "Would create" if DRY_RUN else "Created"
    print(f"Done. {action} {total} data folder(s).")


if __name__ == "__main__":
    main()