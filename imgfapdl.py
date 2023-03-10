import random
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from os import makedirs, path
from time import time
from typing import List, Tuple
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

# Browser Settings (For solving CAPTCHAs)
## Please read the README notes under "IP Blocks" BEFORE modifying anything here.
AUTO_OPEN = False                                                            # change to True if you want the program to automatically open the link to the CAPTCHA.
BROWSER_PATH  = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" # change to the filepath of your browser
INCOGNITO_ARG = "-incognito"                                                 # change to the argument to give to the browser for incognito mode

# characters that can't be used for filenames
DISALLOWED_CHARACTERS = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
SEMI_URL_ENCODING = {
    '\\': '%5C',
    '/': '%2F',
    ':': '%3A',
    '*': '%2A',
    '?': '%3F',
    '"': '%22',
    '<': '%3C',
    '>': '%3E',
    '|': '%7C'
}

# User Agents for spoofing
user_agents = [ 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
] 

IP_BLOCKED = False

def send_get_request(url: str) -> requests.Response:
    """
    Wrapper for sending a GET request to the URL with the appropriate headers.
    """
    global IP_BLOCKED
    if IP_BLOCKED:
        raise RuntimeError("Bot already IP blocked, warning already sent.")
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Referer": "https://www.google.com"
    }

    response = requests.get(
        url,
        headers=headers
    )

    # Check for IP block
    if response.url.endswith("human-verification"):
        IP_BLOCKED = True
        if AUTO_OPEN:
            print("Attempting to open human verification page...")
            runstring = f"\"{BROWSER_PATH}\" {INCOGNITO_ARG} \"{url}\""
            try:
                subprocess.run(runstring, shell=True, check=True)
                print("Opened the human verification page, please solve the CAPTCHA and try again.")
                print(f"If you don't see a CAPTCHA, there is probably an issue with INCOGNITO_ARG. Open {url} manually in an INCOGNITO window and solve the CAPTCHA.")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Could not automatically open human verification page, ensure you have the correct browser filepath and the incognito argument.")
            raise RuntimeError("Bot has been IP blocked for too many requests. Please try running the command again after entering the CAPTCHA.")
        raise RuntimeError(f"Bot has been IP blocked for too many requests. Please manually open {url} in an INCOGNITO window and solve the CAPTCHA, before trying again.")
    
    response.raise_for_status()
    return response


def generate_valid_filename(title: str) -> bool:
    """
    Returns a valid filename given a plain gallery/image title.
    To prevent readability issues, we don't URL encode every character, only certain characters that aren't allowed in filenames.
    """
    filename = title
    for char in DISALLOWED_CHARACTERS:
        filename = filename.replace(char, SEMI_URL_ENCODING[char])
    return filename


def extract_gallery_id(urlstr: str) -> str:
    """
    Returns the Gallery ID from a given `urlstr`.
    This `urlstr` can be of the following formats:
    - `https://www.imagefap.com/gallery/12345678` (From Copying the Link Address from a User)
    - `https://www.imagefap.com/pictures/12345678/Name-Of-Gallery` (From the URL after clicking a Gallery)
    - `https://www.imagefap.com/photo/9876543210/?pgid=&gid=12345678&page=0` (The URL of an image inside a Gallery)
    - `https://www.imagefap.com/gallery.php?gid=12345678` (Link Address from a user's favourites)

    In all the above cases, the gallery ID `12345678` should be extracted appropriately.
    """
    url_struct = urlparse(urlstr)
    if url_struct.scheme == "":
        url_struct = urlparse(f"http://{urlstr}")

    # Ensure correct domain
    if not (url_struct.hostname == "www.imagefap.com" or url_struct.hostname == "imagefap.com"):
        raise RuntimeError(f"Expected a gallery from imagefap.com, instead given link to {urlstr}.")

    # Decide procedure based on path
    path = url_struct.path.split("/")
    path.pop(0)
    queries = url_struct.query.split("&")

    match path[0]:
        case "gallery" | "pictures":
            # https://www.imagefap.com/gallery/{id} or https://www.imagefap.com/pictures/{id}/Name-Of-Gallery
            return path[1]
        case "photo" | "gallery.php":
            # https://www.imagefap.com/photo/9876543210/?pgid=&gid={id}&page=0 or https://www.imagefap.com/gallery.php?gid={id}
            for query in queries:
                if query[:4] == "gid=":
                    return query[4:]  # ID will be the rest of the query
    raise RuntimeError(f"Could not detect gallery ID from {urlstr}.")

def extract_image_id(urlstr: str) -> str:
    """
    Extracts an image ID from a given `urlstr` linking to an image page.
    Usually of the form `https://www.imagefap.com/photo/759249735/...`
    """
    url_struct = urlparse(urlstr)
    if url_struct.scheme == "":
        url_struct = urlparse(f"http://{urlstr}")

    # Ensure correct domain
    if not (url_struct.hostname == "www.imagefap.com" or url_struct.hostname == "imagefap.com"):
        raise RuntimeError(f"Expected an image from imagefap.com, instead given link to {urlstr}.")

    # Decide procedure based on path
    path = url_struct.path.split("/")
    path.pop(0)

    if path[0] == "photo" and len(path) > 1:
        return path[1]
    raise RuntimeError(f"Given url {urlstr} is not an image page.")
    

cached_source_code = None


def get_gallery_source(gallery_id: str):
    """
    Returns the source code of the gallery with `gallery_id` or a cached copy of it.
    """
    global cached_source_code
    if cached_source_code is None:
        # this is the only format we can use without knowing the Gallery's name, and auto-redirects to the `https://www.imagefap.com/pictures/12345678/Name-Of-Gallery` form.
        gallery_url = f"http://www.imagefap.com/gallery.php?gid={gallery_id}"
        response = send_get_request(gallery_url)
        # Add the new view to the redirected URL, since the above URL doesn't redirect to the full page. We want the full page so we can detect all the images at once.
        response = send_get_request(response.url + "?view=2")
        cached_source_code = BeautifulSoup(response.content, 'html.parser')
    return cached_source_code


def get_gallery_name(gallery_id: str) -> str:
    """
    Returns the name of the gallery, given the gallery's ID
    """
    html_code = get_gallery_source(gallery_id)
    title: str = html_code.select("title")[0].text

    # Remove additional text from title
    title = title.replace("Porn Pics & Porn GIFs", "").strip()
    filename = generate_valid_filename(title)

    return filename


def get_image_name(image_id: str, gallery_id: str) -> str:
    """
    Returns the name of the image, given the gallery's ID and the image ID
    """
    html_code = get_gallery_source(gallery_id)
    title: str = html_code.find(
        attrs={'id': image_id}
    ).select('table tr td font i')[0].text

    title = title.strip()
    filename = generate_valid_filename(title)

    return filename



def get_image_page_data(gallery_id: str) -> List[Tuple[str, str]]:
    """
    Parses a given gallery ID, returning a list of tuples representing each image as a tuple (image title, image page source)
    This is constrained by the rules given by `rp`.
    """
    # Cleanly extract all links that link to image pages of the gallery
    links = []
    html_code = get_gallery_source(gallery_id)
    elems = html_code.select('a')

    # extract links from a elems and ignore duplicates
    for elem in elems:
        link = elem.get("href")
        # Skip elements that don't have a `href` attribute
        if link is None:
            continue
        if link.startswith("/"):  # then it's a path, add the domain name
            link = f"https://www.imagefap.com{link}"
        if link not in links:
            links.append(link)

    # For each link, determine if it's a relevant link
    image_page_urls = []
    for link in links:
        url_struct = urlparse(link)
        # Check if it's a photo
        regex_pattern = re.compile("\/photo\/(\w+)\/")
        if regex_pattern.match(url_struct.path) is None:
            continue

        # Check if it has the correct gallery ID
        query_str = f"gid={gallery_id}"
        if query_str not in url_struct.query:
            continue

        image_page_urls.append(link)
    
    # For each link, set the corresponding image title
    image_data = []
    for image_page_url in image_page_urls:
        image_id = extract_image_id(image_page_url)
        image_name = get_image_name(image_id, gallery_id)
        image_data.append(
            (image_name, image_page_url)
        )

    return image_data


def download_image(image_page_data: Tuple[str, str], dl_path: str):
    """
    Downloads an image to `dl_path` given its page URL.
    """
    filename = image_page_data[0]
    image_url = image_page_data[1]

    # Check if file already exists
    if path.isfile(f"{dl_path}/{filename}"):
        print(f"{dl_path}/{filename} already exists, skipping")
        return

    # Extract the image source URL
    response = send_get_request(image_url)
    html_code = BeautifulSoup(response.content, 'html.parser')
    elems = html_code.select("#mainPhoto")

    if len(elems) > 1:
        # TODO: use logging
        print("More than one element with ID 'mainPhoto' detected, using first one.")
    elif len(elems) == 0:
        raise RuntimeError(f"No main photo detected in link {image_url}.")

    elem = elems[0]
    image_src_url = elem.get('src')

    # Write the image file to disk.
    makedirs(dl_path, exist_ok=True)
    image_data = send_get_request(image_src_url).content
    with open(f"{dl_path}/{filename}", 'wb') as f:
        f.write(image_data)
    
    sleep(0.5) # sleep so we don't overwhelm the server.


def main(urlstr: str):
    """
    Main Function
    """
    # Initial Setup
    # Update robot.txt rules for future functions to follow
    rp = RobotFileParser()
    rp.set_url("http://www.imagefap.com/robots.txt")
    rp.read()

    # Ensure URL is allowed
    if rp:
        if not rp.can_fetch("*", urlstr):
            raise RuntimeError(f"Cannot load {urlstr}, site owner has disallowed it for bots.")

    # Extract Images
    print("Preparing to download images...")
    start_t = time()
    gallery_id = extract_gallery_id(urlstr)

    try:
        gallery_name = get_gallery_name(gallery_id)
        image_page_data = get_image_page_data(gallery_id)
        images_downloaded = 0
        images_total = len(image_page_data)
        if images_total == 0:
            raise RuntimeError("No images detected.")
        end_t = time()
        print(f"Preparation took {end_t - start_t:0.2f}s.")

        print("Downloading images...")
        start_t = time()
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(download_image, image_page_data, gallery_name) for image_page_data in image_page_data
            ]

            # Check through futures for exceptions as they complete
            for future in futures:
                try:
                    data = future.result()
                    images_downloaded += 1
                    print(f"Progress: {(images_downloaded / images_total) * 100:0.1f}%", flush=True, end='\r')
                except Exception as e:
                    print("Thread worker reported error:", str(e))

        print(f"Download completed to \"{gallery_name}\". Downloaded {images_downloaded} out of {images_total} images.")
        end_t = time()
        print(f"Download took {end_t - start_t:0.2f}s.")
    except requests.exceptions.RequestException as e:
        raise SystemExit("System Error. ") from e
    except Exception as e:
        raise SystemExit("System error: " + str(e)) from e


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Downloads images from an Imagefap Gallery."
    )
    parser.add_argument(
        "gallery_url",
        type=str,
        help="link of the gallery"
    )

    args = parser.parse_args()
    main(args.gallery_url)
