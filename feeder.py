from time import mktime
from datetime import datetime

import requests
import feedparser
from bs4 import BeautifulSoup


# List of RSS feeds for comics
rss = {
    # "xkcd": "http://xkcd.com/rss.xml",
    # "C&H": "http://feeds.feedburner.com/Explosm",
    # "PhD": "http://phdcomics.com/gradfeed.php",
    # "SMBC": "http://www.smbc-comics.com/rss.php",
    # "NTL": "http://noobtheloser.tumblr.com/rss",
    "PDL": "http://feeds.feedburner.com/PoorlyDrawnLines?format=xml",
}


def get_last_checked_times():
    """ Reads from file the last time a check was made.
    :returns: A datetime object of the last check or None if none was made
    """
    result = {key: None for key in rss}
    try:
        with open("last_check_time.txt", "r") as f:
            for line in f:
                key, t = line.rsplit(" ", 1)
                result[key] = datetime.fromtimestamp(float(t))
        return result
    except FileNotFoundError:
        return result


def set_last_checked_time(last_checks):
    """ Writes to file the current time as the  last checked time. """
    with open("last_check_time.txt", "w") as f:
        for comic in last_checks:
            f.write("{} {}\n".format(comic, last_checks[comic].timestamp()))
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
        comic: name of the comic
    """
    result = dict(post="")

    # Handle those comics that send the image url in their RSS description
    if comic in ["xkcd", "PhD", "SMBC", "NTL"]:
        img = BeautifulSoup(item["summary"], "lxml").find("img")
        img = img or {"src": "https://d30y9cdsu7xlg0.cloudfront.net/png/45592-200.png"}
        result.update({"pre": item["title"], "img": img["src"]})
        if comic == "xkcd":
            result["post"] = "Hover text: " + img["title"]
    elif comic == "PDL":
        img = BeautifulSoup(item["content"][0]["value"], "lxml").find("img")
        img = img or {"src": "https://d30y9cdsu7xlg0.cloudfront.net/png/45592-200.png"}
        result.update({"pre": item["title"], "img": img["src"]})
    elif comic == "C&H":
        # Manually load C&H site to get the image url
        site = requests.get(item["link"]).content.decode()
        img = BeautifulSoup(site, "lxml").find("img", id="main-comic")
        try:
            result.update({"pre": "{}\n{}".format(item["summary"], item["title"]),
                           "img": "http:" + img["src"].split("?t=")[0]})
        except Exception as e:
            result.update({"pre": "C&H seems broken :(", "post": str(e)})

    # Add the comic name
    result["comic"] = comic
    # Add the published date to the
    result["date"] = datetime.fromtimestamp(mktime(item["published_parsed"]))
    # print(item["published"], result["date"])
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
    last_checks = get_last_checked_times()
    for comic in rss:
        print("requesting RSS for", comic)
        feed = feedparser.parse(rss[comic])
        last_date = last_checks[comic]
        for i in feed["items"]:
            data = parse(comic, i)
            last_date = last_date or data["date"]
            last_date = max(last_date, data["date"])
            if last_checks[comic] is None or data["date"] > last_checks[comic]:
                yield data
        last_checks[comic] = last_date
    set_last_checked_time(last_checks)


if __name__ == "__main__":
    print("Running tests...")
    for message in message_creator():
        print(message)
        print()

