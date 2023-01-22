# ImageFap Gallery Download

A rudimentary downloader for ImageFap galleries. 

## Features
- Versatile gallery detection, accepts most URLs that link to ImageFap Galleries
- Takes gallery URL as a command line argument. If necessary, a batch script could be used to download from several galleries at once.
- Downloads multiple images at once with the use of threading.

## Installation
Download [Python 3.11](https://www.python.org/downloads/).

Install the required pip packages:
```
pip install -r requirements.txt
```

## Usage
```
py imgfapdl.py gallery_url
```

- `gallery_url`: The URL to the gallery. The parser is relatively versatile, it's been set to accept most formats of gallery URLs, such as:
    - **Copy Link Address of a Gallery from User Page**: `.../gallery/12345678`
    - **Actual URL of Gallery**: `.../pictures/12345678/Name-Of-Gallery`
    - **URL of an Image inside the Gallery**: `.../photo/9876543210/?pgid=&gid=12345678&page=0`
    - **URL of a Gallery from a User's Favourites**: `.../gallery.php?gid=12345678`.

If you're encountering issues, surround the URL with double-quotes as the command line could have trouble interpreting the URL.
    
The program will then download the gallery to a directory in `imgfapdl`'s root directory, with the same name as the gallery. If the gallery name contains invalid characters (e.g. Windows doesn't allow for filenames with `?` in them), these will be replaced with the [URL-encoded form](https://en.wikipedia.org/wiki/URL_encoding) of that character. The program still keeps other characters like spaces and exclamation marks as part of the filename, to allow for better readability.

## TODO
- Proper logging, with a verbose argument added to the parser to allow for more verbose logging if necessary.
- Proper handling of errors, as of right now I'm too lazy to handle them so someone less used to Python will see some weird cryptic error. Also if filenames are invalid, the program silently fails.
- Tests for the other parts of the code.
- Feature to download images in order, to account for galleries with a story and where images aren't named in numerical order.
