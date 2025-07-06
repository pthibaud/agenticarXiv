from arxiv_client import Client as ArXivClient
from arxiv_client import Query,Category

client = ArXivClient()        
        # Search papers

query=Query(abstract_keywords=["spintronic"], keywords=["spintronic"], categories=[Category.COND_MAT_MES_HALL] , max_results = 25)

print(query)

try :
    papers = client.search(query = query)

finally:
    results = []
    for i, paper in enumerate(papers):
        paper_info = f"### {i}. {"".join(paper.title.split("\n "))}\n\n"
        paper_info += f"**Authors:** {", ".join(paper.authors)}\n\n"
        paper_info += f"**Publication date:** {paper.published}\n\n"
        paper_info += f"**Link:** [{paper.pdf_url}]({paper.pdf_url})\n\n"
        paper_info += f"**Abstract:** {" ".join(paper.summary.split("\n"))}\n"
        results.append(paper_info)
        print(paper_info)