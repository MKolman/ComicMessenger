from time import mktime
from datetime import datetime

import requests
import feedparser
from bs4 import BeautifulSoup


# List of RSS feeds for comics
rss = {
    "xkcd": "http://xkcd.com/rss.xml",
    "C&H": "http://feeds.feedburner.com/Explosm",
    "PhD": "http://phdcomics.com/gradfeed.php",
    "SMBC": "http://www.smbc-comics.com/rss.php"
}


def get_last_checked_time():
    """ Reads from file the last time a check was made.
    :returns: A datetime object of the last check or None if none was made
    """
    try:
        with open("last_check_time.txt", "r") as f:
            return datetime.fromtimestamp(float(f.read()))
    except Exception:
        return None


def set_last_checked_time():
    """ Writes to file the current time as the  last checked time. """
    with open("last_check_time.txt", "w") as f:
        f.write(str(datetime.now().timestamp()))
        f.close()


def parse(comic, item):
    """ Converting specific rss feed item into a dict with data to send
    :params:
        comic: name of the comic we are parsing {'xkcd', 'C&H', 'SMBC',...}
        item: an item instance as returned by the 'feedparser' library
    :returns: one dictionary with keys
        pre: text to be sent first
        img: url link to an image to be sent
        post: text to be sent last
        date: a datetime instance representing the publish date of the comic
    """
    result = dict(post="")

    # Handle those comics that send the image url in their RSS description
    if comic in ["xkcd", "Phd", "SMBC"]:
        img = BeautifulSoup(item["summary"], "lxml").find("img")
        result.update({"pre": item["title"], "img": img["src"]})
        if comic == "xkcd":
            result["post"] = "Hover text: " + img["title"]

    if comic == "C&H":
        # Manually load C&H site to get the image url
        site = requests.get(item["link"]).content.decode()
        img = BeautifulSoup(site, "lxml").find("img", id="main-comic")
        result.update({"pre": "{}\n{}".format(item["summary"], item["title"]),
                       "img": "http:" + img["src"].split("?t=")[0]})

    # Add the published date to the
    result["date"] = datetime.fromtimestamp(mktime(item["published_parsed"]))
    print(item["published"], result["date"])
    if "post" in result:
        result["post"] += "\n" + item["link"]
    else:
        result["post"] = item["link"]
    return result


def message_creator(filter_checked=False):
    """ A generator that yields messages for all new comics
    :params:
        last_check: if True we will filter out comics already checked
    :returns:
        It yields dictionaries describing each new comic
    """
    last_check = get_last_checked_time()
    for comic in rss:
        print("requesting RSS for", comic)
        feed = feedparser.parse(rss[comic])
        for i in feed["items"]:
            data = parse(comic, i)
            if last_check is None or data["date"] > last_check:
                yield data
    set_last_checked_time()