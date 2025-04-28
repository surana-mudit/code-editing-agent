# Python Claude Terminal Chat with Tools

A Python implementation of the terminal-based chat application with Claude using the OpenRouter API and tool-calling capabilities.

## Overview

This Python application creates a terminal interface for chatting with Claude 3.7 Sonnet through OpenRouter and allows Claude to perform actions on your local system through defined tools. The application maintains a conversation history and handles the back-and-forth between the user, Claude, and tool executions.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your OpenRouter API key as an environment variable:
   ```
   export OPENROUTER_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```
   python main.py
   ```

## Available Tools

The application defines three tools that Claude can use:

1. **read_file**: Reads and returns the contents of a specified file
   - Input: A relative file path
   - Output: The file's contents or an error message

2. **list_files**: Lists all files and directories at a given path
   - Input: An optional relative path (defaults to current directory)
   - Output: JSON array of file and directory names

3. **edit_file**: Modifies or creates text files
   - Input: File path, text to replace, and replacement text
   - Can create new files if they don't exist
   - Can replace text in existing files

## Usage

1. Run the application
2. Type messages to Claude in the terminal
3. When Claude wants to use a tool, it will show the tool call and result
4. Continue the conversation based on Claude's responses

## Requirements

- Python 3.7+
- OpenAI Python SDK
- OpenRouter API key
- Internet connection

## Notes

This is a Python implementation of the Go application, offering the same functionality but using the OpenRouter API with Claude through the OpenAI compatibility layer. 