# IMGFap Gallery Download

A rudimentary downloader for IMGFap galleries. 

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