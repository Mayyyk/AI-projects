from pathlib import Path
import difflib
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables for OpenAI
load_dotenv()

class CodeChangeTracker:
    def __init__(self):
        self.client = OpenAI()
        self.last_state_file = "last_state.json"
        self.tracked_extensions = ['.py', '.txt', '.md']  # Files to track
        
    def get_file_contents(self):
        """Get current content of all tracked files"""
        current_state = {}
        for ext in self.tracked_extensions:
            for file in Path('.').glob(f'*{ext}'):
                # Skip certain files
                if any(skip in str(file) for skip in ['__pycache__', '.git', 'last_state.json']):
                    continue
                    
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        current_state[str(file)] = f.read()
                except UnicodeDecodeError:
                    print(f"Skipping binary file: {file}")
                except Exception as e:
                    print(f"Error reading {file}: {str(e)}")
        
        return current_state

    def analyze_changes(self):
        """Compare current files with last saved state"""
        current_state = self.get_file_contents()
        
        # Load previous state if exists
        try:
            if os.path.exists(self.last_state_file):
                with open(self.last_state_file, 'r', encoding='utf-8') as f:
                    previous_state = json.load(f)
            else:
                previous_state = {}
        except Exception:
            previous_state = {}

        # Save current state for next comparison
        with open(self.last_state_file, 'w', encoding='utf-8') as f:
            json.dump(current_state, f, indent=2)

        if not previous_state:
            return "Initial state saved"

        # Compare states and collect changes
        changes = []
        for file in set(current_state.keys()) | set(previous_state.keys()):
            if file not in previous_state:
                changes.append(f"New file created: {file}")
            elif file not in current_state:
                changes.append(f"File deleted: {file}")
            elif current_state[file] != previous_state[file]:
                diff = list(difflib.unified_diff(
                    previous_state[file].splitlines(),
                    current_state[file].splitlines(),
                    fromfile=f'previous/{Path(file).name}',
                    tofile=f'current/{Path(file).name}',
                    lineterm=''
                ))
                if diff:
                    changes.append(f"\nChanges in {file}:\n" + '\n'.join(diff))

        if not changes:
            return "No changes detected"

        # Use GPT to analyze the changes
        prompt = f"""
        Analyze these code and file changes and provide a clear, organized summary:

        {changes}

        Please provide:
        1. A concise bullet-point list of significant changes
        2. Focus on functional changes (ignore formatting changes)
        3. Group related changes together
        4. Highlight any new features or important modifications
        5. Mention any new files or major file changes

        Format the response as markdown-compatible text.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing changes with GPT: {str(e)}\n\nRaw changes:\n" + "\n".join(changes)

def update_progress_file(changes: str):
    """Update PROGRESS.md with latest changes"""
    if changes in ["No changes detected", "Initial state saved"]:
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = f"""
## Update {timestamp}

{changes}

---
"""
    
    progress_file = Path("PROGRESS.md")
    if not progress_file.exists():
        content = "# Development Progress\n\nTrack of changes made to the research script.\n\n"
    else:
        content = progress_file.read_text(encoding='utf-8')
    
    with open(progress_file, "w", encoding='utf-8') as f:
        f.write(content + new_entry) 