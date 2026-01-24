import os
import datetime
import shutil
import re
import subprocess

SOURCE_DIR = "/mnt/d/04_代码/code/sandbox/doc/view"
DEST_DIR = "/mnt/d/04_代码/code/ST-dailyreport"
FILE_PATTERN = r"geoai_world-model_dashboard_.*\.md"

def run_git_commands():
    try:
        os.chdir(DEST_DIR)
        
        subprocess.run(["git", "add", "."], check=True)
        
        today = datetime.date.today().isoformat()
        commit_message = f"Daily report {today}"
        
        status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status_output.strip():
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push", "origin", "master"], check=True)
            print("Successfully pushed to Gitee.")
        else:
            print("No changes to commit.")
            
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"An error occurred during git operations: {e}")

def main():
    today = datetime.date.today().isoformat()
    year = today[:4]
    month = today[5:7]
    day = today[8:10]
    
    target_dir = os.path.join(DEST_DIR, year, month, day)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    files = [f for f in os.listdir(SOURCE_DIR) if re.match(FILE_PATTERN, f)]
    if not files:
        print(f"No matching files found in {SOURCE_DIR}")
        return

    processed_count = 0
    for filename in files:
        if "checkpoint" in filename:
            continue
            
        source_path = os.path.join(SOURCE_DIR, filename)
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = re.sub(r"Date: \d{4}-\d{2}-\d{2}", f"Date: {today}", content)
        
        match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
        if match:
            new_filename = filename.replace(match.group(0), today)
        else:
            name_root, ext = os.path.splitext(filename)
            new_filename = f"{name_root}_{today}{ext}"
            
        dest_path = os.path.join(target_dir, new_filename)
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully generated {dest_path} from {source_path}")
        processed_count += 1
        
    if processed_count > 0:
        run_git_commands()
    else:
        print("No valid files processed (all were checkpoints?).")

if __name__ == "__main__":
    main()
