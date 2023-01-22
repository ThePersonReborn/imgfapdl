# ImageFap Gallery Download

A rudimentary downloader for ImageFap galleries. 

## Features
- Versatile gallery detection, accepts most URLs that link to ImageFap Galleries
- Takes gallery URL as a command line argument. If necessary, a batch script could be used to download from several galleries at once.
- Downloads multiple images at once with the use of threading.
- Detection of IP block, and auto-opening of browser for user to solve CAPTCHA.

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

If you're encountering issues, **surround the URL with double-quotes** as the command line could have trouble interpreting the URL.
    
The program will then download the gallery to a directory in `imgfapdl`'s root directory, with the same name as the gallery. If the gallery name contains invalid characters (e.g. Windows doesn't allow for filenames with `?` in them), these will be replaced with the [URL-encoded form](https://en.wikipedia.org/wiki/URL_encoding) of that character. The program still keeps other characters like spaces and exclamation marks as part of the filename, to allow for better readability.

### IP Blocks
`imgfapdl` sends numerous requests to ImageFap at once -- 1 for the gallery URL, and 2 for every image in the gallery (for the image page, and the source image URL). ImageFap may, upon receiving too many requests from `imgfapdl`, temporarily block the program from downloading images.

The program will alert you as such, and you will have to solve a CAPTCHA challenge to continue downloading images. You can do so manually with the following instructions:
1. Open the link to the gallery you want to access in an INCOGNITO or a PRIVATE window.
    - Emphasis on INCOGNITO. Opening it on your regular browser may not work, as ImageFap probably already knows you're a human based off your regular browsing. The program doesn't have that browsing history, and is determined to be a bot -- so you've gotta help the bot out here.
2. Solve the given CAPTCHA, and click the button to verify it.
3. Repeat the command you gave to `imgfapdl`.

Alternatively, the program can automatically open the human verification link for you (i.e. automatically do step (1.)), for ease of use. *This feature has not been tested on Macs or Linux distributions because I'm fucking lazy*. To configure this, you will need to modify the following variables from Line 14 onwards:
- `AUTO_OPEN`: Program uses this to determine whether to automatically open the link or not. Change this to `True` to enable it.
- `BROWSER_PATH`: 
    - This is the filepath to the browser you wish to use to open the link. 
    - The default path is for Chrome installations on Windows, default installations of other browsers can be viewed below. 
    - Do note your own machine's filepath for the browser may vary, especially if you're not using Windows (sorry, I don't have a Mac to test this, and I'm too lazy to open my Linux distro. :P)
    - **You may need to use double backslashes (`\\`) in place of single backslashes (`\`) when referencing a filepath in Windows**. For Mac/Linux, I think you guys use forward slashes (`/`) so you should be good.
- `INCOGNITO_ARG`: This is the argument given to the command line to open an **incognito** or **private** window in the browser.
    - The default argument is for Chrome only. **This differs for other browsers. Check below if you're not using Chrome.**
    - As mentioned above, this is necessary because opening it in incognito allows for the browsing session to be free of most regular user session data. 

#### Default Browser Settings
Listed here are some default browser paths in **Windows**, and their corresponding incognito arguments. If you're replacing the browser filepath, do remember to replace `INCOGNITO_ARG` too.

**Microsoft Edge**:    
```
BROWSER_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
INCOGNITO_ARG = "-inprivate"
```

**Google Chrome**:    
```
BROWSER_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
INCOGNITO_ARG = "-incognito"
```

**Mozilla Firefox**:    
```
BROWSER_PATH = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
INCOGNITO_ARG = "-private-window"
```

## TODO
- Proper logging, with a verbose argument added to the parser to allow for more verbose logging if necessary.
- Proper handling of errors, as of right now I'm too lazy to handle them so someone less used to Python will see some weird cryptic error. 
- Tests for the other parts of the code.
- Feature to download images in order, to account for galleries with a story and where images aren't named in numerical order.
- Custom filenames and gallery names.