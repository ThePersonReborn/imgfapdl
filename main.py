from urllib.parse import urlparse

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
                    return query[4:] # ID will be the rest of the query
    raise RuntimeError(f"Could not detect gallery ID from {urlstr}.")

def parse_URL(urlstr:str)->str:
    """
    Parses a given URL, validating it and returning the gallery to read from.
    """

    # Ensure URL is up

    # Extract ID
    gallery_id = extract_ID(urlstr)

    return f"http://www.imagefap.com/gallery/{gallery_id}"
