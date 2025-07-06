#!/usr/bin/env python3
"""
arXiv MCP server implementatie met de officiële MCP Python SDK.
"""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context

from arxiv_client import Client as ArXivClient
from arxiv_client import Query

# Create an MCP server instance
mcp = FastMCP("arXiv Knowledge")


@mcp.tool()
async def search_arxiv_papers(query: str, max_results: int = 10) -> str:
    """
    Search for scientific papers on arXiv.
    
    Args:
    query: The query (keywords, authors, category, etc.)
    max_results: Maximum number of results to return
    
    Returns:
    A formatted list of relevant papers
    """
    try:
        # Create an arXiv client
        client = ArXivClient()        
        # Search papers
        # papers = await client.search(query, max_results = max_results)
        papers = await client.search(query = Query(query, max_results = max_results),page_size=4)
        
        # No results?
        if not papers:
            return f"No papers found for the search: '{query}'"
        
        # Format the results
        results = []
        for i, paper in enumerate(papers, 1):
            paper_info = f"### {i}. {paper['title']}\n"
            paper_info += f"**Authors:** {paper['authors']}\n"
            paper_info += f"**Publication date:** {paper['published']}\n"
            paper_info += f"**Link:** {paper['pdf_url']}\n"
            paper_info += f"**Abstract:** {paper['summary']}\n"
            results.append(paper_info)
        
        header = f"# Search results for: '{query}'\n\n"
        return header + "\n\n".join(results)
    
    except Exception as e:
        return f"Error when searching for papers: {str(e)}"


@mcp.resource("arxiv://help")
def arxiv_help() -> str:
    """
    Resource with help information on using the arXiv MCP server.
    """
    help_text = """
    # ArXiv Knowledge Server Help
    
    This is an MCP server that gives you access to scientific papers on arXiv.
    
    ## Available tools
    
    ### search_arxiv_papers
    
    Searches for papers on arXiv and returns the most relevant results.
    
    Parameters:
    - query: Search query (keywords, authors, categories, etc.).
    - max_results: Maximum number of results (default 10)
    
    Example usage:
    ```
    Can you find papers on spintronics published in 2023?
    ```
    
    ## Tips for effective searching
    
    - Use specific keywords for more accurate results
    - Combine author names with topics
    - Specify categories for targeted searches
    """
    return help_text


if __name__ == "__main__":
    mcp.run()