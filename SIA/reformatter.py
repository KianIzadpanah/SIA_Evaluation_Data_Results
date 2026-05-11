import os
import shutil
import re

# source_dir = f"/workspace/visual_analogy/evaluation/Qualitative_SIA_results/2edits_eval"
# dest_dir = f"/workspace/Qualitative_experiment/edit2_eval"

# source_dir = f"/workspace/visual_analogy/evaluation/Qualitative_SIA_results/2edits_non_creature_eval"
# dest_dir = f"/workspace/Qualitative_experiment/edit2_non_creature_eval"

# source_dir = f"/workspace/visual_analogy/evaluation/Qualitative_SIA_results/3edits_eval"
# dest_dir = f"/workspace/Qualitative_experiment/edit3_eval"

source_dir = f"/workspace/visual_analogy/evaluation/Qualitative_SIA_results/3edits_non_creature_eval"
dest_dir = f"/workspace/Qualitative_experiment/edit3_non_creature_eval"

# source_dir = f"/workspace/visual_analogy/evaluation/Qualitative_SIA_results/4edits_eval"
# dest_dir = f"/workspace/Qualitative_experiment/edit4_eval"

def remaining_edits(text: str, n: int) -> str:
    # Find all e1, e2, e3... inside the string
    found = set(re.findall(r"e\d+", text))

    # Build remaining edits
    remaining = []
    for i in range(1, n + 1):
        e_name = f"e{i}"
        if e_name not in found:
            remaining.append(f"edit{i}")
    return "_".join(remaining)

def is_allowed_file(rel_path: str) -> bool:
    """
    Return True if the file should be copied, False otherwise.
    Allowed conditions:
      - The full relative path (including directories) contains e1, e2, e3, or e4.
      - OR the base filename is exactly "base_lora.png".
    Excluded if the base filename contains "grid.png".
    """
    filename = os.path.basename(rel_path)
    
    # Exclude any file with "grid.png" in its name
    if "grid.png" in filename:
        return False
    
    # Allowed if the path contains e1, e2, e3, or e4
    if any(f"e{i}" in rel_path for i in range(1, 5)):
        return True
    
    # Allowed if it's exactly base_lora.png
    if filename == "base_lora.png":
        return True
    
    return False

def flatten_directory(source_dir: str, dest_dir: str, instructions_cnt: int = 4):
    """
    Flatten files: first directory name + '_' + (processed remaining path).
    Only allowed files are copied.
    """
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist.")

    os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, start=source_dir)

            # --- FILTER ---
            if not is_allowed_file(rel_path):
                print(f"Skipped (not allowed): {src_path}")
                continue

            # Split at the first path separator
            parts = rel_path.split(os.sep, 1)

            if len(parts) == 1:
                first_dir = ""
                rest = parts[0]
            else:
                first_dir = parts[0]
                rest = parts[1]

            # Process the "rest" part
            descs = remaining_edits(rest, instructions_cnt)

            # Build the new name
            if first_dir:
                new_name = first_dir + "_" + descs + ".png"
            else:
                new_name = descs + ".png"

            dst_path = os.path.join(dest_dir, new_name)
            shutil.copy2(src_path, dst_path)
            print(f"Copied: {src_path} -> {dst_path}")

if __name__ == "__main__":
    flatten_directory(source_dir, dest_dir)