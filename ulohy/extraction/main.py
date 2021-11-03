#!/usr/bin/env python3

import time
from typing import NamedTuple, Optional, Dict, Tuple, List, Any

import requests

import os
import bs4
from urllib.parse import urlparse

class FullScrap(NamedTuple):
    # TUTO TRIDU ROZHODNE NEMEN
    linux_only_availability: List[str]
    most_visited_webpage: Tuple[int, str]
    changes: List[Tuple[int, str]]
    params: List[Tuple[int, str]]
    tea_party: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            'linux_only_availability': self.linux_only_availability,
            'most_visited_webpage': self.most_visited_webpage,
            'changes': self.changes,
            'params': self.params,
            'tea_party': self.tea_party
        }


def download_webpage(url: str, *args, **kwargs) -> requests.Response:
    """
    Download the page and returns its response by using requests.get
    :param url: url to download
    :return: requests Response
    """
    # TUTO FUNKCI ROZHODNE NEMEN
    print('GET ', url)
    return requests.get(url, *args, **kwargs)


def get_linux_only_availability(base_url: str) -> List[str]:
    """
    Finds all functions that area available only on Linux systems
    :param base_url: base url of the website
    :return: all function names that area available only on Linux systems
    """
    # Tuto funkci implementuj
    pass


def get_most_visited_webpage(base_url: str) -> Tuple[int, str]:
    """
    Finds the page with most links to it
    :param base_url: base url of the website
    :return: number of anchors to this page and its URL
    """
    # Tuto funkci implementuj
    pass


def get_changes(base_url: str) -> List[Tuple[int, str]]:
    """
    Locates all counts of changes of functions and groups them by version
    :param base_url: base url of the website
    :return: all counts of changes of functions and groups them by version, sorted from the most changes DESC
    """
    # Tuto funkci implementuj
    pass


def get_most_params(base_url: str) -> List[Tuple[int, str]]:
    """
    Finds the function that accepts more than 10 parameters
    :param base_url: base url of the website
    :return: number of parameters of this function and its name, sorted by the count DESC
    """
    # Tuto funkci implementuj
    pass


def find_secret_tea_party(base_url: str) -> Optional[str]:
    """
    Locates a secret Tea party
    :param base_url: base url of the website
    :return: url at which the secret tea party can be found
    """
    # Tuto funkci implementuj
    pass


def scrap_all(base_url: str) -> FullScrap:
    """
    Scrap all the information as efficiently as we can
    :param base_url: base url of the website
    :return: full web scrap of the Python docs
    """
    # Tuto funkci muzes menit, ale musi vracet vzdy tyto data
    scrap = FullScrap(
        linux_only_availability=get_linux_only_availability(base_url),
        most_visited_webpage=get_most_visited_webpage(base_url),
        changes=get_changes(base_url),
        params=get_most_params(base_url),
        tea_party=find_secret_tea_party(base_url)
    )
    return scrap


# === custom funcitons begin here ===
class Cache:
    """
    A cache object which saves 
    """
    def __init__(self, base_url: str, output_path: str) -> None:
        self.base_url = base_url
        self.base_url_parsed = urlparse(base_url)
        self.output_path = output_path
        self.output: Dict[str, requests.Response] = {}

    def check_downloaded(self) -> bool:
        """
        Checks, if the output path exists.
        :return: boolean
        """
        return os.path.exists(self.output_path)

    def recursively_download_webpage(self) -> None:
        """
        After making the initial request, search for all urls from the same
        site and then get all these pages as well.

        All the sites and URLs are then saved to `self.output`.
        """
        initial_request = download_webpage(self.base_url)
        if not initial_request.__str__() == "<Response [200]>":
            return
        soup = bs4.BeautifulSoup(initial_request.text, "html.parser")

        # download all the webpages available from the start url
        visited_urls = []
        errored_urls = []
        url_stack = []
        initial_a_tags = soup.find_all("a")

        # TODO: rework required
        # MAJOR REWORK REQUIRED
        for elem in initial_a_tags:
            link = elem.get("href")
            if link.startswith("https://") or link.startswith("#") \
                or link in self.output.keys():
                continue
            url_stack.append(link)

        while url_stack:
            current = url_stack.pop(0)
            if current.startswith("../"):
                current = current.lstrip("../")
            current = self.base_url + current
            parsed_url = urlparse(current)
            current = self.base_url + parsed_url.path[1:]
            response = download_webpage(current)
            if response.__str__() != "<Response [200]>":
                errored_urls.append(current)
                print("bad response")
                continue
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            tags = soup.find_all("a")
            for each in tags:
                new_url = each.get("href")
                new_parsed = urlparse(self.base_url + new_url)
                print(new_parsed.path)
                new_url = self.base_url + new_parsed.path[1:]
                new_parsed = urlparse(new_url)
                if new_parsed.netloc != self.base_url_parsed.netloc \
                    or new_url in visited_urls or new_url in url_stack:
                    continue
                url_stack.append(new_url)
            self.output[current] = response
            visited_urls.append(current)
    
        print(len(self.output))

def main() -> None:
    """
    Do a full scrap and print the results
    :return:
    """
    # Tuto funkci klidne muzes zmenit podle svych preferenci :)
    import json

    URL = "https://python.iamroot.eu/"
    time_start = time.time()
    print(json.dumps(scrap_all(URL).as_dict()))
    print('took', int(time.time() - time_start), 's')
    # === testing ===
    cache = Cache(URL, "./output/") 
    cache.recursively_download_webpage()
    # url = "https://python.iamroot.eu/library/code.html#module-code"
    # parser = urlparse(url)
    # print(parser)


if __name__ == '__main__':
    main()
