import datetime
import sys
import threading
import time
import requests
import os
import tempfile
import subprocess
import re
import platform
from typing import Optional, Tuple

class NaturalLanguageCodeTool:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = 'https://api.openai.com/v1/chat/completions'
        self.risky_keywords = {
            'rm', 'del', 'shutil', 'os.remove', 'os.rmdir', 'os.unlink',
            'kill', 'format', 'chmod', 'admin',
            'sudo', 'reboot', 'shutdown', 'halt', 'poweroff',
            # 'subprocess'
        }
        self.isSafetyCheckEnabled = True
        self.log_dir = 'logs'
        os.makedirs(self.log_dir, exist_ok=True)

    def execute_code(self, code: str, command: str) -> Tuple[bool, str]:
        """Executes code with safety checks and proper output capture"""
        if self.isSafetyCheckEnabled and not self._validate_code_safety(code):
            return False, "Code blocked by safety checks"

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_data = {
            'timestamp': timestamp,
            'command': command,
            'code': code,
            'output': '',
            'error': '',
            'success': False
        }

        try:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w+') as temp_file:
                temp_file.write(self._generate_safe_wrapper(code))
                temp_file_path = temp_file.name

            result = subprocess.run(
                ['python', temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )

            log_data['output'] = result.stdout.strip()
            log_data['error'] = result.stderr.strip()
            log_data['success'] = result.returncode == 0

        except subprocess.TimeoutExpired:
            log_data['error'] = "Execution timed out (30 seconds)"
        except Exception as e:
            log_data['error'] = f"Execution failed: {str(e)}"
        finally:
            if temp_file_path:
                os.remove(temp_file_path)

        self._save_execution_log(log_data)
        return log_data['success'], log_data['output'] or log_data['error']

    def _generate_safe_wrapper(self, code: str) -> str:
        """Wraps code in safety checks and output redirection"""
        return f'''# -*- coding: utf-8 -*-
import sys
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

try:
    f_out = StringIO()
    f_err = StringIO()
    
    with redirect_stdout(f_out), redirect_stderr(f_err):
{self._indent_code(code, 8)}
except Exception as e:
    print(f"Error: {{str(e)}}", file=sys.stderr)
finally:
    print(f_out.getvalue())
    print(f_err.getvalue(), file=sys.stderr)
'''

    def _indent_code(self, code: str, spaces: int) -> str:
        return '\n'.join([' ' * spaces + line for line in code.split('\n')])

    def _validate_code_safety(self, code: str) -> bool:
        """Check for potentially dangerous operations"""
        code_lower = code.lower()
        risky_found = []

        for keyword in self.risky_keywords:
            # Use regex to match the keyword as a standalone word or as part of a function call
            pattern = rf'\b{re.escape(keyword)}\b'
            if re.search(pattern, code_lower):
                risky_found.append(keyword)

        if risky_found:
            print(code)
            print("Potential risky operation detected with keywords:", ', '.join(risky_found))
            confirmation = input("Execute this risky code? (y/N): ").lower()
            return confirmation == 'y'
        return True

    def _save_execution_log(self, log_data: dict):
        """Save structured execution logs"""
        log_file = os.path.join(self.log_dir, 
                               f"log_{log_data['timestamp']}.log")
        with open(log_file, 'w') as f:
            f.write(f"COMMAND: {log_data['command']}\n")
            f.write(f"TIMESTAMP: {log_data['timestamp']}\n")
            f.write(f"SUCCESS: {log_data['success']}\n")
            f.write("\n=== GENERATED CODE ===\n")
            f.write(log_data['code'] + '\n')
            f.write("\n=== OUTPUT ===\n")
            f.write(log_data['output'] + '\n')
            f.write("\n=== ERRORS ===\n")
            f.write(log_data['error'] + '\n')

    def run(self, natural_language_command: str):
        code = self.get_python_code(natural_language_command)
        stop_animation.set()
        animation_thread.join()
        if code:
            success, output = self.execute_code(code, natural_language_command)
            if success:
                print(f"Success: {output}")
            else:
                print(f"Error: {output}")

    def get_python_code(self, command: str) -> Optional[str]:
        """Get generated code with improved prompt"""
        improved_prompt = f"""Convert this natural language command to Python code following these rules:
1. Output ONLY the code wrapped in ```python markers
2. Target Windows 10 environment
3. Installed packages: requests, webbrowser, pyautogui, keyboard, pyperclip
4. Safety requirements:
   - Never use sudo/admin privileges
   - Handle exceptions properly
   - Prefer built-in libraries over external APIs
   - Use webbrowser for URLs instead of direct requests
   - For web scraping: use requests + BeautifulSoup (assume installed)
5. Add progress indicators for long operations
6. Show desktop notifications using plyer for UI interactions
7. If user asks a general knowledge question and you know the correct answer, just print the answer. If the answer REALLY requires latest info, you can use the browser.
8. The generated code will be auto-executed, so dont expect any user input in the generated code. Don't expect user to replace any url, variable, etc in the code. Dont put any example.com url.
9. Current platform: {platform.system()} {platform.release()}

Command: {command}"""

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        data = {
            'model': 'gpt-4o',
            'messages': [{
                'role': 'system',
                'content': 'You are a Python expert that generates safe, production-quality code.'
            }, {
                'role': 'user',
                'content': improved_prompt
            }],
            'temperature': 0.2,
            'max_tokens': 1000
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            return self._extract_code_block(content)
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None

    def _extract_code_block(self, content: str) -> Optional[str]:
        """Extract code from markdown code blocks"""
        match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
        return match.group(1).strip() if match else None
    
def loading_animation(stop_event):
    while not stop_event.is_set():
        for char in '|/-\\':
            sys.stdout.write(f'\r {char}')
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write(f'\r  \r')
    sys.stdout.flush()


if __name__ == '__main__':
    tool = NaturalLanguageCodeTool()
    print("Natural Language Command Tool (Ctrl+C to exit)")
    
    while True:
        try:
            command = input("\nEnter command: ").strip()
            if not command: continue
            
            stop_animation = threading.Event()
            animation_thread = threading.Thread(
                target=loading_animation, 
                args=(stop_animation,),
                daemon=True
            )
            animation_thread.start()
            
            
            tool.run(command)
            print("----------------------------------------")

        except KeyboardInterrupt:
            print("\nExiting...")
            break