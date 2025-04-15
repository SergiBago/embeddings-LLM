import requests
from bs4 import BeautifulSoup
import markdownify
import os
from urllib.parse import urljoin, urlparse

# Define base URL
BASE_URL = "https://www.fib.upc.edu/en/"

# Define language prefixes to ignore (ignores base language pages but keeps subpages)
LANG_PREFIXES = ["/ca", "/es"]

#Ignorar elements que no es puguin convertir a markdown
IGNORE_TYPES = [".rss", ".py"]

# Folder to store Markdown files
SAVE_FOLDER = "markdown"
#os.makedirs(SAVE_FOLDER, exist_ok=True)

# Track visited URLs to avoid duplicates
visited_urls = set()

pending_urls=[]

def url_to_filepath(url):
    """
    Convert a URL to a valid Markdown file path with subfolders.
    Example: "https://www.fib.upc.edu/en/mobility/outgoing/mobility-calendar"
    → "fib_markdown/en/mobility/outgoing/mobility-calendar.md"
    """
    path = urlparse(url).path.strip("/")

    if not path or path == "/":
        return os.path.join(SAVE_FOLDER, "index.md")

    # Create the full folder structure
    full_path = os.path.join(SAVE_FOLDER, path)
    if not full_path.endswith(".md"):
        full_path += ".md"

    # Ensure the folder exists before saving the file
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    return full_path


def should_ignore_url(url):
    """Ignore page with strange types"""
    for type in IGNORE_TYPES:
        if url.endswith(type):
            return True

    """Check if the URL is just a language version of the main page."""
    for prefix in LANG_PREFIXES:
        if url.endswith(prefix) or prefix+"/" in url:
            return True
    return False


def scrape_page(url):
    """Extracts content from a webpage and converts it to Markdown."""
    if should_ignore_url(url):
        print(f"Ignoring page: {url}")
        return None

    if url in visited_urls:
        return None

    print(f"Scraping: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Process links before converting to Markdown
    for a_tag in soup.find_all("a", href=True):
        original_link = a_tag["href"]
        absolute_link = urljoin(BASE_URL, original_link)

        # Convert internal links to Markdown files
        if absolute_link.startswith(BASE_URL):
            md_filepath = url_to_filepath(absolute_link)
            md_relative_path = os.path.relpath(md_filepath, SAVE_FOLDER)

            # Add the URL to pending_urls so it will be downloaded later
            if absolute_link not in visited_urls and absolute_link not in pending_urls:
                pending_urls.append(absolute_link)

            a_tag["href"] = f"./{md_relative_path}"  # Update the link to be relative


    # Process image sources before converting to Markdown
    for img_tag in soup.find_all("img", src=True):
        original_src = img_tag["src"]
        absolute_src = urljoin(BASE_URL, original_src)
        img_tag["src"] = absolute_src

    # Convert HTML to Markdown
    md_content = markdownify.markdownify(str(soup.body), heading_style="ATX")

    # Save the Markdown file in the correct subfolder
    md_filepath = url_to_filepath(url)
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Mark as visited
    visited_urls.add(url)

    return md_filepath


def downloadWebsite(url, folder):
    SAVE_FOLDER = folder
    # Start with the main page

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    BASE_URL = hostname.replace('.', '_')

    pending_urls = [url]

    while pending_urls:
        current_url = pending_urls.pop(0)
        filename = scrape_page(current_url)

        if filename:
            # Extract new links from the downloaded page
            with open(filename, "r", encoding="utf-8") as f:
                md_text = f.read()

            soup = BeautifulSoup(md_text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                absolute_link = urljoin(BASE_URL, a_tag["href"])

                # Avoid adding language-only URLs
                if absolute_link.startswith(BASE_URL) and absolute_link not in visited_urls and not should_ignore_url(
                        absolute_link):
                    pending_urls.append(absolute_link)

    print("✅ Download complete!")
