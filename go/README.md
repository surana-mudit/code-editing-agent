# Claude Terminal Chat with Tools

A Go application that enables terminal-based conversations with Claude (Anthropic's LLM) with tool-calling capabilities.

## Overview

This application creates a terminal interface for chatting with Claude 3.7 Sonnet and allows Claude to perform actions on your local system through defined tools. The application maintains a conversation history and handles the back-and-forth between the user, Claude, and tool executions.

## Core Components

### Agent

The Agent manages the conversation flow between the user and Claude. It:
- Collects user input from the terminal
- Sends messages to the Claude API
- Processes Claude's responses
- Executes tools when Claude requests them
- Maintains the conversation history

### Tools

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

### Technical Implementation

- Uses the Anthropic Go SDK to communicate with Claude's API
- Implements JSON schema generation for tool definitions
- Handles conversation state management
- Formats terminal output with color coding for different message types

## Usage

1. Run the application
2. Type messages to Claude in the terminal
3. When Claude wants to use a tool, it will show the tool call and result
4. Continue the conversation based on Claude's responses

## Requirements

- Go programming environment
- Anthropic API key (set as an environment variable)
- github.com/anthropics/anthropic-sdk-go
- github.com/invopop/jsonschema

## Notes

This is a demonstration of Claude's tool-use capabilities in a terminal environment, allowing Claude to read, list, and modify files on your local system under user supervision. 