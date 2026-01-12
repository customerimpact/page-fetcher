import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def scrape_single_page(url):
    """
    Fetches a single URL and converts it to Markdown.
    Returns specific structure:
    {
        "url": url,
        "status": "success" or "error",
        "content" or "error_message": ...
    }
    """
    try:
        # Use a generic user agent to avoid simple blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simple cleanup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Convert to markdown
        markdown_content = md(str(soup), heading_style="ATX")
        
        # Add a title header from the URL or page title
        title = soup.title.string if soup.title else url
        final_markdown = f"# Source: {url}\n\n## {title}\n\n{markdown_content}\n\n---\n\n"
        
        return {
            "url": url,
            "status": "success",
            "content": final_markdown
        }
        
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "error_message": str(e)
        }
