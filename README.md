# ImageFap Gallery Download

A rudimentary downloader for ImageFap galleries. 

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
    - **Copy Link Address from User**: `.../gallery/12345678`
    - **Actual URL of Gallery**: `.../pictures/12345678/Name-Of-Gallery`
    - **URL of an Image inside the Gallery**: `/photo/9876543210/?pgid=&gid=12345678&page=0`
    - **URL from a User's Favourites**: `/gallery.php?gid=12345678`.
    
The program will then download the gallery to a directory in `imgfapdl`'s root directory, with the same name as the gallery.
