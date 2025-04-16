from .webToMarkdown import *
from .CreateEmbeddingsDb import *
import os

SAVE_FOLDER = "markdown"

def extractWebInfo(url):
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    base_folder = hostname.replace('.', '_')
    folder = os.path.join(SAVE_FOLDER, base_folder)
    os.makedirs(folder, exist_ok=True)
    downloadWebsite(url, folder)
    process_folder_files(folder)

    return "Scraping complete"