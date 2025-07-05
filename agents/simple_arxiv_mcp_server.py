#!/usr/bin/env python3
import asyncio
import json
import sys
import traceback
from typing import Dict, List, Any, Optional

from urllib import request, parse

def fetch_arxiv_papers(query: str, max_results: int = 3):
    """
    Fetches papers from arXiv using a simple API call.
    """
    import feedparser
    base_url = "https://export.arxiv.org/api/query?"
    url = f"{base_url}search_query={parse.quote(query)}&start=0&max_results={max_results}"
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [author.name for author in entry.authors],
            "link": entry.link
        })
    return results

class ArxivMCPServerStdio:
    """
    A simplified MCP server that communicates via stdin/stdout.
    Implements the MCP protocol without dependency on the mcp module.
    """
    
    def __init__(self):
        self.tools = {
            "search_arxiv_papers": {
                "type": "function",
                "function": {
                    "name": "search_arxiv_papers",
                    "description": "Search for papers on Arxiv",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an incoming MCP message and returns a response.
        """
        try:
            if message.get("type") == "capabilities":
                return self.handle_capabilities()
            elif message.get("type") == "tool_call":
                return await self.handle_tool_call(message)
            else:
                return {
                    "type": "error",
                    "error": {
                        "message": f"Unsupported message type: {message.get('type')}"
                    }
                }
        except Exception as e:
            traceback.print_exc()
            return {
                "type": "error",
                "error": {
                    "message": f"Error handling message: {str(e)}"
                }
            }
    
    def handle_capabilities(self) -> Dict[str, Any]:
        """
        Returns the capabilities of this MCP server.
        """
        return {
            "type": "capabilities",
            "capabilities": {
                "tools": list(self.tools.values())
            }
        }
    
    async def handle_tool_call(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a tool_call message and executes the requested function.
        """
        tool_call = message.get("tool_call", {})
        tool_name = tool_call.get("name")
        
        if tool_name != "search_arxiv_papers":
            return {
                "type": "error",
                "error": {
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        params = tool_call.get("parameters", {})
        query = params.get("query")
        max_results = params.get("max_results", 3)
        
        if not query:
            return {
                "type": "error",
                "error": {
                    "message": "Missing required parameter: query"
                }
            }
        
        # Perform the search
        try:
            papers = fetch_arxiv_papers(query, max_results)
            return {
                "type": "tool_result",
                "tool_result": {
                    "content": papers
                }
            }
        except Exception as e:
            traceback.print_exc()
            return {
                "type": "error",
                "error": {
                    "message": f"Error searching Arxiv: {str(e)}"
                }
            }
    
    async def read_message(self) -> Optional[Dict[str, Any]]:
        """
        Reads a JSON message from stdin.
        """
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                return None
            return json.loads(line)
        except json.JSONDecodeError:
            print("Error: Invalid JSON received", file=sys.stderr)
            return None
    
    def write_message(self, message: Dict[str, Any]) -> None:
        """
        Writes a JSON message to stdout.
        """
        json_str = json.dumps(message)
        print(json_str, flush=True)
    
    async def run(self) -> None:
        """
        Starts the MCP server and processes messages until a shutdown signal is received.
        """
        print(f"🚀 Server is starting...", file=sys.stderr)
        try:
            while True:
                message = await self.read_message()
                if message is None:
                    break
                
                response = await self.handle_message(message)
                self.write_message(response)
        except Exception as e:
            print(f"Error in MCP server: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

async def main():
    server = ArxivMCPServerStdio()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())