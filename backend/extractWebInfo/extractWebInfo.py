from .webToMarkdown import *
from .CreateEmbeddingsDb import *
import os

SAVE_FOLDER = "markdown"

def extractWebInfo(url, task_id, progress_dict):
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    #base_folder = hostname.replace('.', '_')
    #folder = os.path.join(SAVE_FOLDER, base_folder)
    folder = os.path.join(SAVE_FOLDER, hostname)
    os.makedirs(folder, exist_ok=True)
    downloadWebsite(url, folder, task_id, progress_dict)
    if(url.endswith("/")):
        url = url[:-1]
    process_folder_files(url, folder, task_id, progress_dict)

    return "Scraping complete"