from arxiv_client import Client as ArXivClient
from arxiv_client import Query,Category

client = ArXivClient()        
        # Search papers

query=Query(abstract_keywords=["spintronic"], keywords=["spintronic"], categories=[Category.COND_MAT_MES_HALL] , max_results = 100)

try :
    papers = client.search(query = query)

finally:
    results = []
    abstracts = []
    for i, paper in enumerate(papers):
        paper_info = f"### {i}. {"".join(paper.title.split("\n "))}\n\n"
        paper_info += f"**Authors:** {", ".join(paper.authors)}\n\n"
        paper_info += f"**Publication date:** {paper.published}\n\n"
        paper_info += f"**Link:** [{paper.pdf_url}]({paper.pdf_url})\n\n"
        paper_info += f"**Abstract:** {" ".join(paper.summary.split("\n"))}\n"
        results.append(paper_info)
        abstracts.append(paper.summary)
        
        print(paper_info)
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from config import MISTRAL_CONFIG
from mistralai import Mistral

api_key = MISTRAL_CONFIG.get("api_key")
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = model,
    messages = [
        {
            "role": "system",
            "content": """
            You are an AI librarian classifying research articles.

            Here are {len(abstracts)} abstracts:
            {abstracts}

            Group them by topic and suggest folder names for each group.
            """
        }
    ]
)

print(chat_response.choices[0].message.content)