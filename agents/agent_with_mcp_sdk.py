#!/usr/bin/env python3
"""
Agent used by the MCP server with the official MCP Python SDK.
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

# Import MCP client functionalities
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Path to the MCP server script
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "arxiv_mcp_server_sdk.py")


class arXivAgent:
    """An agent that interacts with the ArXiv MCP server to find papers."""

    def __init__(self, api_key: str):
        """Initialise the agent with OpenAI client."""
        self.openai_client = OpenAI(api_key=api_key,base_url="https://api.openai.com/v1")
        self.server_params = StdioServerParameters(
            command=sys.executable,  # Python executable
            args=[MCP_SERVER_PATH],  # MCP server script
            env=os.environ.copy(),  # Provide current environment
        )

    async def run_conversation(self, user_question: str) -> str:
        """
        Conduct a conversation with the user, using the MCP server for tools.
        """
        try:
            # Start de MCP client
            async with stdio_client(self.server_params) as (read_stream, write_stream):
                # Create a client session
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialise the connection
                    await session.initialize()

                    # Get available tools
                    tools = await session.list_tools()

                    # Convert MCP tools to OpenAI tool format
                    openai_tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description or "",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        param.name: {
                                            "type": param.type,
                                            "description": param.description or "",
                                        }
                                        for param in tool.parameters
                                    },
                                    "required": [
                                        param.name
                                        for param in tool.parameters
                                        if param.required
                                    ],
                                },
                            },
                        }
                        for tool in tools
                    ]

                    # Create the messages for the OpenAI API
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that can search for scientific papers on arXiv. Use the search_arxiv_papers tool to find papers related to the user's query.",
                        },
                        {"role": "user", "content": user_question},
                    ]

                    # Make the API call to OpenAI
                    response = self.openai_client.chat.completions.create(
                        model=OLLAMA_CONFIG.get("default_model") or "mistral",
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto",
                    )

                    # Process the answer
                    assistant_message = response.choices[0].message

                    # Add the assistant message with tool_calls
                    messages.append(
                        {
                            "role": "assistant",
                            "content": assistant_message.content or "",
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments,
                                    },
                                }
                                for tc in (assistant_message.tool_calls or [])
                            ]
                            if assistant_message.tool_calls
                            else None,
                        }
                    )

                    # Process tool calls if present
                    if assistant_message.tool_calls:
                        for tool_call in assistant_message.tool_calls:
                            # Get the tool parameters
                            function_name = tool_call.function.name
                            arguments = json.loads(tool_call.function.arguments)

                            # Roep de tool aan via de MCP client
                            tool_result = await session.call_tool(
                                function_name, arguments=arguments
                            )

                            # Add the result to the messages
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": tool_result,
                                }
                            )

                        # Ask OpenAI for a definitive answer
                        second_response = self.openai_client.chat.completions.create(
                            model = OLLAMA_CONFIG.get("default_model") or "mistral", 
                            messages = messages
                        )

                        return second_response.choices[0].message.content

                    # If there are no tool calls, return the original answer
                    return assistant_message.content or "No response from assistant"

        except Exception as e:
            return f"Error running agent: {str(e)}"

