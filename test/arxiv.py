import os
import sys

# Add parent directory to system path for module imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from arxiv_client import Client as ArXivClient
from arxiv_client import Query, Category
from config import MISTRAL_CONFIG
from mistralai import Mistral

# Instantiate the client
client = ArXivClient()        

# Define search parameters
query = Query(
    abstract_keywords=["spintronic"],
    keywords=["spintronic"],
    categories=[Category.COND_MAT_MES_HALL],
    max_results=10
)

try:
    # Perform search query
    papers = client.search(query=query)
finally:
    results = []
    abstracts = []
    with open("output.md", "w") as file:
        for i, paper in enumerate(papers):
            paper_info = (
                f"### {i}. {''.join(paper.title.split('\n'))}\n\n"
                f"**Authors:** {', '.join(paper.authors)}\n\n"
                f"**Publication date:** {paper.published}\n\n"
                f"**Link:** [{paper.pdf_url}]({paper.pdf_url})\n\n"
                f"**Abstract:** {' '.join(paper.summary.split('\n'))}\n"
            )
            results.append(paper_info)
            abstracts.append(paper.summary)
            print(paper_info, file=file)

    prompt = (
        f"""
You are an AI librarian classifying research articles and an expert in academic paper organization.

Here are {len(abstracts)} abstracts:
{abstracts}

Classify them by topic and suggest folder names for each topic.
"""
    )

    # Initialize the Mistral client
    api_key = MISTRAL_CONFIG.get("api_key")
    model = MISTRAL_CONFIG.get("default_model")

    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": """
- Classify these abstracts into folders.
- For each folder, group all the abstracts and summarize them together in a single sentence.
- Print the folder name in "**bold**" then write the abstract numbers in this folder as an array and write the summary, all in a single line.
"""
            }
        ]
    )

with open("classified.md", "w") as file:
    print(chat_response.choices[0].message.content, file=file)
