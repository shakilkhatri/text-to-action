import datetime
import requests
import os
import tempfile

class NaturalLanguageCodeTool:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = 'https://api.openai.com/v1/chat/completions'

    def execute_code(self, code):
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Save the code to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name

        # Create a unique log file name with a timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file_path = os.path.join(log_dir, f'log_{timestamp}.log')
        with open(log_file_path, 'w') as log_file:
            log_file.write(f'{code}')  # Write the code and a newline

        # Execute the code
        os.system(f'python "{temp_file_path}"')

        # Clean up the temporary file
        os.remove(temp_file_path)

    def run(self, natural_language_command):
        code = self.get_python_code(natural_language_command)
        if code:
            self.execute_code(code)

    def get_python_code(self, natural_language_command):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        data = {
            'model': 'gpt-4o',
            'messages': [
                {'role': 'user', 'content': f'Convert this natural language command to Python code. output should be only the code and NOTHING ELSE. Not even formatting. just plain code. note I am using windows 10 laptop. requests, webbrowser, pyautogui, keyboard packages are installed. do not try to use any api that requires api key. use an api ONLY IF you are sure about it. if not, access it using the browser. give priority to coding than using pyautogui as coding is more reliable than blindly controlling the pc. if you want to browse the web, instead of directly opening a url from your knowledge, do google search, click on first link and extract data from there. except for the very common websites. If you are taking control of the PC, during that period, display an overlay notification on top of everything.   : \n\n command: {natural_language_command}'}
            ],
        }
        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            if 'choices' in response_json:
                code = response_json['choices'][0].get('message', {}).get('content', '').strip()
                return code
            else:
                print(f"Response did not contain 'choices': {response_json}")
                return None
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")
            return None



if __name__ == '__main__':
    tool = NaturalLanguageCodeTool()
    print("Press 'Ctrl+C' to stop.")

    while True:
        try:
            natural_language_command = input("What can I help you with? ")
            tool.run(natural_language_command)
        except KeyboardInterrupt:
            print("\nOperation stopped by user.")
            break
