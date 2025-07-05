#!/usr/bin/env python3
"""
Agent qui utilise le serveur MCP arXiv simplifié.
"""

import asyncio
import json
import os
import subprocess
import sys

from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from config import OPENAI_CONFIG

# Path to the MCP server script
MCP_SERVER_PATH = os.path.join(os.path.dirname(
    __file__), "simple_arxiv_mcp_server.py")

class arXivAgent:
    """An agent that uses the arXiv MCP server to find scientific papers."""

    def __init__(self, openai_api_key: str):
        """Initialize the agent with OpenAI client."""
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.mcp_server_process = None

    async def start_mcp_server(self) -> subprocess.Popen:
        """Start the MCP server as a subprocess and return the process handle."""
        # Ensure the script is executable
        if not os.access(MCP_SERVER_PATH, os.X_OK):
            os.chmod(MCP_SERVER_PATH, 0o755)

        # Start the server as a subprocess
        process = subprocess.Popen(
            [sys.executable, MCP_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=1  # Line buffered
        )
        self.mcp_server_process = process
        return process

    async def send_receive_message(self, process: subprocess.Popen, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to the MCP server and wait for a response."""
        # Send the message
        json_message = json.dumps(message) + "\n"
        if process.stdin is None:
            print("Error: process stdin is None", file=sys.stderr)
            return None

        process.stdin.write(json_message)
        process.stdin.flush()

        # Read the response
        if process.stdout is None:
            print("Error: process stdout is None", file=sys.stderr)
            return None

        response_line = await asyncio.get_event_loop().run_in_executor(None, process.stdout.readline)
        if not response_line:
            return None

        try:
            return json.loads(response_line)
        except json.JSONDecodeError:
            print(
                f"Error: Invalid JSON response: {response_line}", file=sys.stderr)
            return None

    async def get_server_capabilities(self, process: subprocess.Popen) -> List[Dict[str, Any]]:
        """Request the capabilities of the MCP server."""
        message = {"type": "capabilities"}
        response = await self.send_receive_message(process, message)

        if response and response.get("type") == "capabilities":
            return response.get("capabilities", {}).get("tools", [])
        return []

    async def call_tool(self, process: subprocess.Popen, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Call a tool on the MCP server."""
        message = {
            "type": "tool_call",
            "tool_call": {
                "name": tool_name,
                "parameters": parameters
            }
        }

        response = await self.send_receive_message(process, message)

        if response and response.get("type") == "tool_result":
            return response.get("tool_result", {}).get("content", "No content returned")
        elif response and response.get("type") == "error":
            return f"Error: {response.get('error', {}).get('message', 'Unknown error')}"
        else:
            return "Unknown response from MCP server"

    async def run_conversation(self, user_question: str, model: str) -> str:
        """
        Conduct a conversation with the user, utilizing the MCP server for tools.
        """
        # Start de MCP server
        process = await self.start_mcp_server()

        try:
            # Retrieve server capabilities
            tools = await self.get_server_capabilities(process)
            if not tools:
                return "Failed to get MCP server capabilities"

            # Create the messages for the OpenAI API
            messages = [
                {"role": "system", "content": "You are a helpful assistant that can search for scientific papers on arXiv. Use the search_arxiv_papers tool to find papers related to the user's query."},
                {"role": "user", "content": user_question}
            ]

            # Make the API call to OpenAI
            response = self.openai_client.chat.completions.create(
                model = model,
                messages = messages,
                tools = tools,
                tool_choice = "auto"
            )

            # Process the response
            assistant_message = response.choices[0].message

            # Add the assistant message with tool_calls
            assistant_msg = {"role": "assistant", "content": assistant_message.content or ""}
            # Only add tool_calls if your OpenAI client and API version support it
            if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
                # If tool_calls is expected to be a string, serialize it as JSON
                assistant_msg["tool_calls"] = json.dumps([
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in assistant_message.tool_calls
                ])

            messages.append(assistant_msg)

            # Process tool calls if present
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    # Retrieve the tool parameters
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Call the tool
                    tool_result = await self.call_tool(process, function_name, arguments)

                    # Add the result to the messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

                # Ask OpenAI for a final answer
                second_response = self.openai_client.chat.completions.create(
                    model = OPENAI_CONFIG.get("default_model", "gpt-4-turbo"),
                    messages = messages
                )

                return second_response.choices[0].message.content or ""

            # If there are no tool calls, return the original answer
            return assistant_message.content or "No response from assistant"

        finally:
            # Shut down the MCP server
            if process.poll() is None:  # If the process is still running
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    process.kill()  # Force termination if terminate does not work
