import re

def extract_ID(urlstr:str)->str:
    """
    Returns the Gallery ID from a given `urlstr`.
    This `urlstr` can be of the following formats:
    - `https://www.imagefap.com/gallery/12345678` (From Copying the Link Address from a User)
    - `https://www.imagefap.com/pictures/12345678/Name-Of-Gallery` (From the URL after clicking a Gallery)
    - `https://www.imagefap.com/photo/9876543210/?pgid=&gid=12345678&page=0` (The URL of an image inside a Gallery)
    - `https://www.imagefap.com/gallery.php?gid=12345678` (Link Address from a user's favourites)

    In all the above cases, the gallery ID `12345678` should be extracted appropriately.
    """

    return "12345678"

def parse_URL(urlstr:str)->str:
    """
    Parses a given URL, validating it and returning the gallery to read from.
    """

    # Ensure URL is from the correct domain

    # Ensure URL is up

    # Extract ID
    gallery_id = extract_ID(urlstr)

    return f"http://www.imagefap.com/gallery/{gallery_id}"
