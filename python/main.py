import json
import os
import sys
import re
from pathlib import Path
import readline  # Enables better CLI input experience
from typing import Dict, List, Callable, Any, Optional, Union, Tuple

from openai import OpenAI
import jsonschema

# Colorized output helpers
BLUE = "\033[94m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

class Agent:
    def __init__(
        self, 
        client: OpenAI, 
        get_user_message: Callable[[], Tuple[str, bool]], 
        tools: List[Dict]
    ):
        self.client = client
        self.get_user_message = get_user_message
        self.tools = tools
        self.tool_functions = {
            "read_file": read_file,
            "list_files": list_files,
            "edit_file": edit_file
        }

    def run(self):
        """Run the conversation loop."""
        conversation = []

        print("Chat with OpenRouter LLM (use 'ctrl-c' to quit)")

        read_user_input = True
        try:
            while True:
                if read_user_input:
                    print(f"{BLUE}You{RESET}: ", end="")
                    user_input, ok = self.get_user_message()
                    if not ok:
                        break

                    user_message = {"role": "user", "content": user_input}
                    conversation.append(user_message)

                message = self.run_inference(conversation)
                
                # Add the assistant's message to the conversation
                conversation.append({
                    "role": "assistant",
                    "content": message.get("content", ""),
                    "tool_calls": message.get("tool_calls", [])
                })

                # Process any tool calls
                tool_results = []
                if message.get("tool_calls"):
                    for tool_call in message["tool_calls"]:
                        result = self.execute_tool(
                            tool_call["id"], 
                            tool_call["function"]["name"], 
                            json.loads(tool_call["function"]["arguments"])
                        )
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result
                        })
                
                if not tool_results:
                    read_user_input = True
                    continue
                
                # Add tool results to conversation and continue without new user input
                conversation.extend(tool_results)
                read_user_input = False
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        return None

    def execute_tool(self, id: str, name: str, input_data: Dict) -> str:
        """Execute a tool with given parameters."""
        if name not in self.tool_functions:
            return "Tool not found"

        print(f"{GREEN}tool{RESET}: {name}({json.dumps(input_data)})")
        
        try:
            response = self.tool_functions[name](input_data)
            return response
        except Exception as e:
            return str(e)

    def run_inference(self, conversation: List[Dict]) -> Dict:
        """Send the conversation to the LLM and get a response."""
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=conversation,
                tools=self.tools,
                max_tokens=1024
            )
            
            # Extract the message from the response
            message = response.choices[0].message
            
            # Handle the message content
            if message.content:
                print(f"{YELLOW}Assistant{RESET}: {message.content}")
            
            # Return the message as a dictionary
            return message.model_dump()
        
        except Exception as e:
            print(f"Error during inference: {e}")
            return {"content": f"Error: {str(e)}"}


# Tool functions
def read_file(input_data: Dict) -> str:
    """Read the contents of a file."""
    if "path" not in input_data:
        return "Path parameter is required"
    
    try:
        with open(input_data["path"], "r") as file:
            return file.read()
    except Exception as e:
        return str(e)

def list_files(input_data: Dict) -> str:
    """List files and directories at a given path."""
    dir_path = input_data.get("path", ".")
    
    try:
        files = []
        for p in Path(dir_path).glob("**/*"):
            rel_path = p.relative_to(dir_path)
            if p.is_dir():
                files.append(str(rel_path) + "/")
            else:
                files.append(str(rel_path))
        
        return json.dumps(files)
    except Exception as e:
        return str(e)

def edit_file(input_data: Dict) -> str:
    """Edit a file by replacing text or creating a new file."""
    if "path" not in input_data:
        return "Path parameter is required"
    
    path = input_data["path"]
    old_str = input_data.get("old_str", "")
    new_str = input_data.get("new_str", "")
    
    if old_str == new_str:
        return "old_str and new_str must be different"
    
    try:
        # Check if file exists
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
            
            if old_str == "":
                return f"File already exists, and old_str is empty"
            
            # Replace the content
            new_content = content.replace(old_str, new_str)
            
            if content == new_content:
                return "old_str not found in file"
            
            with open(path, "w") as file:
                file.write(new_content)
            
            return "OK"
        else:
            # Create new file if it doesn't exist and old_str is empty
            if old_str == "":
                # Create parent directories if they don't exist
                parent_dir = os.path.dirname(path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                
                with open(path, "w") as file:
                    file.write(new_str)
                
                return f"Successfully created file {path}"
            else:
                return f"File {path} does not exist"
    
    except Exception as e:
        return str(e)

# Tool definitions with their schemas
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The relative path of a file in the working directory."
                }
            },
            "required": ["path"]
        }
    }
}

LIST_FILES_TOOL = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List files and directories at a given path. If no path is provided, lists files in the current directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional relative path to list files from. Defaults to current directory if not provided."
                }
            }
        }
    }
}

EDIT_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": "Make edits to a text file. Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other. If the file specified with path doesn't exist, it will be created.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file"
                },
                "old_str": {
                    "type": "string",
                    "description": "Text to search for - must match exactly and must only have one match exactly"
                },
                "new_str": {
                    "type": "string",
                    "description": "Text to replace old_str with"
                }
            },
            "required": ["path", "old_str", "new_str"]
        }
    }
}

def main():
    # Check for OpenRouter API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable is not set")
        print("Please set your OpenRouter API key with: export OPENROUTER_API_KEY=your_key_here")
        sys.exit(1)
    
    # Initialize OpenAI client with OpenRouter base URL
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    # Set up user input handler
    def get_user_message():
        try:
            user_input = input()
            return user_input, True
        except (EOFError, KeyboardInterrupt):
            return "", False
    
    # Define tools
    tools = [READ_FILE_TOOL, LIST_FILES_TOOL, EDIT_FILE_TOOL]
    
    # Create agent and run conversation
    agent = Agent(client, get_user_message, tools)
    agent.run()

if __name__ == "__main__":
    main() 