import os
import re
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup


def get_ar5iv_link(url: str) -> str:
    """
    Turns an arxiv link into a ar5iv link for HTML processing.

    Args:
        url (str): The original arxiv URL (e.g., https://arxiv.org/pdf/...).

    Returns:
        str: The corresponding ar5iv URL.
    """
    if url.startswith("https://ar5iv.labs.arxiv.org/html/"):
        return url
    
    # Updated regex to handle different arxiv URL formats (e.g. /abs/, /pdf/)
    match = re.search(r"arxiv\.org\/(?:pdf|abs)\/([\w+.-]+)", url)
    if not match:
        raise ValueError(f"{url} is not a valid arxiv link!")

    paper_id = match.group(1)
    # Remove .pdf if it exists
    if paper_id.endswith('.pdf'):
        paper_id = paper_id[:-4]
        
    return f"https://ar5iv.labs.arxiv.org/html/{paper_id}"


def get_html_page(url: str) -> str:
    """
    Fetches HTML content from a URL, using a local cache to avoid repeated requests.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page.
    """
    cache_dir = "html_cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Create a simple cache key from the URL
    cache_key = "".join(c for c in url if c.isalnum()) + ".html"
    file_path = os.path.join(cache_dir, cache_key)

    if os.path.exists(file_path):
        print(f"Cache hit for {url}. Reading from {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"Cache miss for {url}. Fetching from web...")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            
            html_content = response.text
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return html_content
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            raise


def get_title_from_html(html: str) -> Optional[str]:
    """
    Extracts the document title from the ar5iv HTML.

    Args:
        html (str): The HTML content of the page.

    Returns:
        Optional[str]: The extracted title, or None if not found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    element = soup.find(class_="ltx_title_document")
    if element:
        # Join fragments and strip whitespace for a clean title
        title = " ".join(element.get_text(strip=True).split())
        return title
    return None


def get_paragraphs_from_html(html: str) -> Tuple[List[str], List[str]]:
    """
    Extracts paragraphs from the ar5iv HTML.

    Returns both a clean text version for the LLM and the original HTML
    for potential rendering (though rendering is removed in this version).

    Args:
        html (str): The HTML content of the page.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing:
            - A list of LLM-readable paragraphs (clean text).
            - A list of the original HTML paragraphs.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Start searching for paragraphs after the main title
    title_element = soup.find(class_="ltx_title_document")
    
    search_area = title_element if title_element else soup
    elements = search_area.find_all_next(class_="ltx_p")

    if not elements: # Fallback if no paragraphs are found after the title
        elements = soup.find_all(class_="ltx_p")

    original_html = [str(e) for e in elements]
    llm_readable = []

    for e in elements:
        # Create a copy to avoid modifying the original soup object
        e_copy = BeautifulSoup(str(e), 'html.parser')
        
        # Replace <math> tags with their 'alttext' for better LLM consumption
        for math_tag in e_copy.find_all('math'):
            alttext = math_tag.get("alttext")
            if alttext:
                # Wrap in $ to signify it's a formula
                math_tag.replace_with(f"${alttext.strip()}$")
        
        text = e_copy.get_text(separator=' ', strip=True)
        if text: # Only add non-empty paragraphs
            llm_readable.append(text)

    return llm_readable, original_html