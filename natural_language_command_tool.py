import requests
import os

class NaturalLanguageCommandTool:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = 'https://api.openai.com/v1/chat/completions'

    def execute_command(self, command):
        os.system(command)

    def run(self, natural_language_command):
        command = self.get_command_prompt_command(natural_language_command)
        print(f'Executing Command Prompt command: {command}')
        self.execute_command(command)

    def get_command_prompt_command(self, natural_language_command):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'user', 'content': f'Convert this natural language command to Command Prompt command. output should be only the command and NOTHING ELSE. Not even formatting. just plain command: {natural_language_command}'}
            ],
            'max_tokens': 60,
        }
        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            if 'choices' in response_json:
                command = response_json['choices'][0].get('message', {}).get('content', '').strip()
                return command
            else:
                print(f"Response did not contain 'choices': {response_json}")
                return None
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")
            return None
if __name__ == '__main__':
    tool = NaturalLanguageCommandTool()
if __name__ == '__main__':
    tool = NaturalLanguageCommandTool()
    natural_language_command = input("Please enter your natural language command: ")
    tool.run(natural_language_command)
