# Natural Language Command Tool

This project provides a tool that converts natural language commands to Python code using the OpenAI API and executes them.

## Features

- Convert natural language commands to Python code.
- Execute the generated Python code automatically while logging the execution.

## Requirements

- Python 3.x
- `requests` library

## Setup

1. Install the required library:

   ```bash
   pip install requests
   ```

2. Set up your OpenAI API key in your environment variables under the name `OPENAI_API_KEY`.

## Usage

You can run the tool by executing the `main.py` script after setting up your API key. You will be prompted to enter your natural language command, which will be converted to Python code and executed.
