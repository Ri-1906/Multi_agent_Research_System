from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from tavily import TavilyClient
# from rich import print
load_dotenv()

tavily_client =  TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def webSearch(query : str) -> str :
    '''Search the web for recent and reliable information for query asked  
    Return titles, url and snippet.
    '''
    res = tavily_client.search(query = query , max_results= 7)
    out = []

    for r in res['results']:
        out.append(
            f"Title : {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n--------\n".join(out)
# webSearch.invoke("recent news about AI")



@tool
def scrape(url: str) ->str:
    """Fetch a web page and return its readable text content.

    Use this after webSearch when you need the full text of a result page.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return f"Error fetching page: {error}"

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()

    page_text = soup.get_text(separator=" ", strip=True)
    return page_text[:3000] or "No readable text found on this page."




