import random
import re
from concurrent.futures import ThreadPoolExecutor
from os import makedirs
from time import time
from typing import List
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

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
user_agents = [ 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
] 

def send_get_request(url: str) -> requests.Response:
    """
    Wrapper for sending a GET request to the URL with the appropriate headers.
    """
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
        raise RuntimeError("Bot has been IP blocked for too many requests.")
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


cached_source_code = None


def get_gallery_source(gallery_id: str):
    """
    Returns the source code of the gallery with `gallery_id` or a cached copy of it.
    """
    global cached_source_code
    if cached_source_code is None:
        # this is the only format we can use without knowing the Gallery's name, and auto-redirects to the `https://www.imagefap.com/pictures/12345678/Name-Of-Gallery` form.
        gallery_url = f"http://www.imagefap.com/gallery.php?gid={gallery_id}&view=2"
        request = send_get_request(gallery_url)
        request.raise_for_status()
        cached_source_code = BeautifulSoup(request.content, 'html.parser')
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


def get_image_URLs(gallery_id: str) -> List[str]:
    """
    Parses a given URL, validating it and returning the image URLs to extract.
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

    return image_page_urls


def download_image(image_url: str, dl_path: str):
    """
    Downloads an image to `dl_path` given its page URL.
    """
    # Extract the image source URL
    request = send_get_request(image_url)
    request.raise_for_status()
    html_code = BeautifulSoup(request.content, 'html.parser')
    elems = html_code.select("#mainPhoto")

    if len(elems) > 1:
        # TODO: use logging
        print("More than one element with ID 'mainPhoto' detected, using first one.")
    elif len(elems) == 0:
        raise RuntimeError(f"No main photo detected in link {image_url}.")

    elem = elems[0]
    image_title = elem.get('title')
    image_src_url = elem.get('src')

    filename = generate_valid_filename(image_title)

    # Write the image file to disk.
    makedirs(dl_path, exist_ok=True)
    image_data = send_get_request(image_src_url).content
    with open(f"{dl_path}/{filename}", 'wb') as f:
        f.write(image_data)


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
        image_urls = get_image_URLs(gallery_id)
        images_downloaded = 0
        images_total = len(image_urls)
        if images_total == 0:
            raise RuntimeError("No images detected.")
        end_t = time()
        print(f"Preparation took {end_t - start_t:0.2f}s.")

        print("Downloading images...")
        start_t = time()
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(download_image, image_url, gallery_name) for image_url in image_urls
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
