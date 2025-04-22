import requests
from bs4 import BeautifulSoup
import markdownify
import os
from urllib.parse import urljoin, urlparse
import json

# Configuration paths
CONFIG_FILE = "config/config.json"
# Load configurations
with open(CONFIG_FILE, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Define language prefixes to ignore (ignores base language pages but keeps subpages)
LANG_PREFIXES =  config["ignore_langs"]

#Ignorar elements que no es puguin convertir a markdown
IGNORE_TYPES = config["ignore_types"]

DOWNLOADED_FILES = "data/downloaded.txt"
PENDING_URLS_FILE = "data/pending_urls.txt"

visited_urls = set()

def load_downloaded_urls():
    global visited_urls
    if not os.path.exists(DOWNLOADED_FILES):
        os.makedirs(os.path.dirname(DOWNLOADED_FILES), exist_ok=True)
        open(DOWNLOADED_FILES, "w", encoding="utf-8").close()
        visited_urls = set()
    with open(DOWNLOADED_FILES, "r", encoding="utf-8") as f:
        visited_urls = set(line.strip() for line in f.readlines())

def save_downloaded_url(url):
    visited_urls.add(url)
    with open(DOWNLOADED_FILES, "a", encoding="utf-8") as f:
        f.write(url + "\n")

load_downloaded_urls()

pending_urls = []

def load_pending_urls():
    global pending_urls
    if not os.path.exists(PENDING_URLS_FILE):
        os.makedirs(os.path.dirname(PENDING_URLS_FILE), exist_ok=True)
        open(PENDING_URLS_FILE, "w", encoding="utf-8").close()
        pending_urls = []
    else:
        with open(PENDING_URLS_FILE, "r", encoding="utf-8") as f:
            pending_urls = [line.strip() for line in f.readlines()]

def save_pending_urls(url):
    pending_urls.append(url)
    with open(PENDING_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

load_pending_urls()

# Folder to store Markdown files
SAVE_FOLDER = ""
#os.makedirs(SAVE_FOLDER, exist_ok=True)


MAX_FILES =  config["max_files"]
if(MAX_FILES == None):
    MAX_FILES = 500

def url_to_filepath(url, is_pdf=False):
    """
    Convert a URL to a valid file path with subfolders.
    - If it's a webpage → save as Markdown (`.md`).
    - If it's a PDF → save with the original extension (`.pdf`).
    """
    path = urlparse(url).path.strip("/")
    if not path or path == "/":
        return os.path.join(SAVE_FOLDER, "_index.md")

    # Ensure the full folder structure exists
    full_path = os.path.join(SAVE_FOLDER, path)
    if is_pdf:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path  # Keep .pdf extension

    if not full_path.endswith(".md"):
        full_path += ".md"

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path


def should_ignore_url(url):
    """Ignore page with strange types"""
    for type in IGNORE_TYPES:
        if url.endswith(type):
            return True

    """Check if the URL is just a language version of the main page."""
    for prefix in LANG_PREFIXES:
        pre = "/" + prefix
        if url.endswith(pre) or pre+"/" in url:
            return True
    return False


def download_pdf(url):
    """Downloads a PDF and saves it in the correct subfolder."""
    pdf_path = url_to_filepath(url, is_pdf=True)
    if not pdf_path.endswith(".pdf"):
        pdf_path += ".pdf"

    # Check if PDF was already downloaded
    if os.path.exists(pdf_path):
        return pdf_path

    print(f"Downloading PDF: {url}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(pdf_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)
        return pdf_path
    except requests.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
        return None


def scrape_page(url, base_url):
    """Extracts content from a webpage and converts it to Markdown."""

    print(f"Scraping: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Process links before converting to Markdown
    for a_tag in soup.find_all("a", href=True):
        original_link = a_tag["href"]
        absolute_link = urljoin(base_url, original_link)

        # Handle PDFs separately
        if absolute_link.lower().endswith(".pdf"):
            pdf_path = download_pdf(absolute_link)
            if pdf_path:
                a_tag["href"] = f"./{os.path.relpath(pdf_path, SAVE_FOLDER)}"  # Update PDF link
            continue

        # Convert internal links to Markdown files
        if absolute_link.startswith(base_url):
            md_filepath = url_to_filepath(absolute_link)
            md_relative_path = os.path.relpath(md_filepath, SAVE_FOLDER)

            # Add the URL to pending_urls so it will be downloaded later
            if absolute_link not in visited_urls and absolute_link not in pending_urls and not should_ignore_url(
                        absolute_link):
                save_pending_urls(absolute_link)

            a_tag["href"] = f"./{md_relative_path}"  # Update the link to be relative


    # Process image sources before converting to Markdown
    for img_tag in soup.find_all("img", src=True):
        original_src = img_tag["src"]
        absolute_src = urljoin(base_url, original_src)
        img_tag["src"] = absolute_src

    # Convert HTML to Markdown
    md_content = markdownify.markdownify(str(soup.body), heading_style="ATX")

    # Save the Markdown file in the correct subfolder
    md_filepath = url_to_filepath(url)
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    return md_filepath


def downloadWebsite(url, folder, task_id, progress_dict):
    global SAVE_FOLDER
    global visited_urls
    global pending_urls

    SAVE_FOLDER = folder

    load_downloaded_urls()

    base_url = url
    pending_urls.append(base_url)

    count = 0

    while pending_urls and count < MAX_FILES:
        current_url = pending_urls.pop(0)

        if current_url in visited_urls:
            continue  # Ya descargada, la saltamos

        if should_ignore_url(current_url):
            print(f"Ignoring page: {current_url}")
            continue

        this_task = f"Downloading {current_url}..."
        progress_dict[task_id]['text'] += "\n" + this_task

        try:
            scrape_page(current_url, base_url)

        except Exception as e:
            print(str(e))

        #if filename:

            # Extract new links from the downloaded page
         #   with open(filename, "r", encoding="utf-8") as f:
          #      md_text = f.read()

            #soup = BeautifulSoup(md_text, "html.parser")

            #for a_tag in soup.find_all("a", href=True):
            #    absolute_link = urljoin(base_url, a_tag["href"])

            #    # Avoid adding language-only URLs
            #    if absolute_link.startswith(base_url) and absolute_link not in visited_urls and not should_ignore_url(
            #            absolute_link):
            #        save_pending_urls(absolute_link)

        # Mark as visited
        save_downloaded_url(current_url)

        progress_dict[task_id]['text'] = progress_dict[task_id]['text'].replace(
            this_task,
            f"✅ Downloaded {current_url}"
        )
        count += 1

    print("✅ Download complete!")
