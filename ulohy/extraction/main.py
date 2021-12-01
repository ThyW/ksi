#!/usr/bin/env python3

from typing import NamedTuple, Optional, Dict, Tuple, List, Any

import requests

import os
import bs4
from urllib.parse import urlparse, urljoin
import pickle


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


def get_linux_only_availability(cache: "Cache") -> Tuple[int, List[str]]:
    """
    Finds all functions that area available only on Linux systems
    :param base_url: base url of the website
    :return: all function names that area available only on Linux systems
    """
    ret = list()
    lines = ""
    with open("linux_only_availablity_parsed", "w") as file:
        for _, response in cache.output.items():
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            fn_matches = soup.find_all("dl", class_="function")
            for match in fn_matches:
                dt = match.find("dt").get("id")
                av_match = match.find("p", class_="availability")
                if av_match and dt:
                    # remove "Availability:"
                    av_without = av_match.text.removeprefix("Availability: ")
                    if ("Unix" or "Linux" in av_without) and\
                        (("Windows" not in av_without)
                         and ("Android" not in av_without) and ("SSL"
                         not in av_without) and ("BSD" not in av_without)):
                        s = f"function_name: {dt} | av: {av_without}\n"
                        lines = lines + s
                        ret.append(dt)
        file.writelines(lines)
    file.close()
    return (len(ret), ret)


def get_most_visited_webpage(cache: "Cache") -> Tuple[int, str]:
    """
    Finds the page with most links to it
    :cache data structure with cashed urls and responses
    :return most visited url with the amount of time visited
    """
    m = max(cache.url_count.values())
    r = ""
    for url, value in cache.url_count.items():
        if value == m:
            r = url
    return (m, r)


def get_changes(cache: "Cache") -> List[Tuple[int, str]]:
    """
    Locates all counts of changes of functions and groups them by version
    :param base_url: base url of the website
    :return: all counts of changes of functions and groups them by version,
     sorted from the most changes DESC
    """
    # Tuto funkci implementuj
    changes: Dict[str, int] = dict()
    for _, response in cache.output.items():
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        version_added = soup.find_all("div", class_="versionadded")
        version_changed = soup.find_all("div", class_="versionchanged")

        # handle version added
        for each_added in version_added:
            found = each_added.find("span", class_="versionmodified added")
            if not found is None:
                # print(f"added: {found.text}")
                parsed = found.text.removeprefix("New in version ")
                if ":" in parsed:
                    parsed = parsed.removesuffix(": ")
                split = parsed.split(".")
                split = split[0] + "." + split[1]
                if split[0] != "3":
                    continue
                else:
                    if changes.get(split) is not None:
                        changes[split] += 1
                    else:
                        changes[split] = 1

        for each_changed in version_changed:
            found = each_changed.find_all("span", class_="versionmodified changed")
            for each in found:
                # print(f"changed: {each.text}")
                parsed = each.text.removeprefix("Changed in version ")
                if ":" in parsed:
                    parsed = parsed.removesuffix(": ")
                split = parsed.split(".")
                split = split[0] + "." + split[1]
                if split[0] != "3":
                    continue
                else:
                    if changes.get(split) is not None:
                        changes[split] += 1
                    else:
                        changes[split] = 1

    l = list()
    s = sorted(changes.items(), key=lambda x: x[1])
    s = dict(s)
    for each in s.items():
        l.append((each[1], each[0]))
    return l[::-1]


def get_most_params(cache: "Cache") -> List[Tuple[int, str]]:
    """
    Finds the function that accepts more than 10 parameters
    :param base_url: base url of the website
    :return: number of parameters of this function and its name,
     sorted by the count DESC
    """
    # Tuto funkci implementuj
    l: List[Tuple[int, str]] = list()

    for response in cache.output.values():
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        functions = soup.find_all("dl", class_="function")
        for function in functions:
            dt = function.find("dt")
            name = dt.get("id")
            params = dt.find_all("em", class_="sig-param")
            if len(params) > 10:
                l.append((len(params), name))
    return list(sorted(l, key=lambda x: x[0]))[::-1]


def find_secret_tea_party(cache: "Cache") -> Optional[str]:
    """
    Locates a secret Tea party
    :param base_url: base url of the website
    :return: url at which the secret tea party can be found
    """
    # Tuto funkci implementuj
    for each in cache.errored:
        if str(each[1]) == "<Response [418]>":
            return each[1].text.removeprefix("Location: ")


def scrap_all(cache: "Cache") -> FullScrap:
    """
    Scrap all the information as efficiently as we can
    :param base_url: base url of the website
    :return: full web scrap of the Python docs
    """
    # Tuto funkci muzes menit, ale musi vracet vzdy tyto data
    scrap = FullScrap(
        linux_only_availability=get_linux_only_availability(cache),
        most_visited_webpage=get_most_visited_webpage(cache),
        changes=get_changes(cache),
        params=get_most_params(cache),
        tea_party=find_secret_tea_party(cache)
    )
    return scrap


# === custom funcitons and classes begin here ===
class Cache:
    """
    A cache object which saves
    """
    def __init__(self, base_url: str, output_path: str) -> None:
        self.base_url = base_url
        self.base_url_parsed = urlparse(base_url)
        self.output_path = output_path
        self.output: Dict[str, requests.Response] = {}
        self.errored: List[Tuple[str, requests.Response]] = list()
        self.url_count: Dict[str, int] = {}

    def check_downloaded(self) -> bool:
        """
        Checks, if the output path exists.
        :return: boolean
        """
        return os.path.exists(self.output_path)

    def valid_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc) and bool(parsed_url.scheme)

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

        for elem in initial_a_tags:
            link = elem.get("href")
            if link.startswith("https://") or link.startswith("#") \
               or link in self.output.keys():
                continue

            # this is correct because we checked :)
            normalised_link = self.base_url + link
            url_stack.append(normalised_link)

        # go through all the urls, checking the current one, downloading it and
        # looking for all the links within it, adding them to the list of urls
        # to visit
        while url_stack:
            current = url_stack.pop(0)
            if self.url_count.get(current) is None:
                self.url_count[current] = 1
            else:
                self.url_count[current] += 1
            domain = urlparse(current).netloc

            request = download_webpage(current)

            if "[200]" not in str(request):
                errored_urls.append((current, request))
                continue
            soup = bs4.BeautifulSoup(request.text, "html.parser")
            tags = soup.find_all("a")
            for each in tags:
                new_url = each.get("href")
                if new_url == "" or new_url is None:
                    continue
                new_url = urljoin(current, new_url)
                parsed_url = urlparse(new_url)
                new_url = parsed_url.scheme + "://" \
                    + parsed_url.netloc + parsed_url.path
                if not self.valid_url(new_url):
                    continue
                if new_url in visited_urls: 
                    continue
                if domain not in new_url:
                    continue
                if (new_url in visited_urls or new_url in errored_urls \
                   or new_url in url_stack) and new_url != current:
                    if self.url_count.get(new_url) is None:
                        self.url_count[new_url] = 1
                    else:
                        self.url_count[new_url] += 1
                if new_url in visited_urls or new_url in errored_urls \
                   or new_url in url_stack:
                    continue
                else:
                    url_stack.append(new_url)
            self.output[current] = request
            visited_urls.append(current)

        self.errored = errored_urls
        print(f"output len: {len(self.output)}")

    # save all found urls to file
    def save(self) -> None:
        with open(self.output_path, "w") as file:
            lines = "\n".join(self.output.keys())
            file.writelines(lines)
            file.close()

    # load a all urls from a file
    def load_file(self, path: str) -> None:
        with open(path, "r") as save_file:
            for line in save_file.read().splitlines():
                sp = line.split(";")
                self.output[sp[0]] = Pair(download_webpage(sp[0]), nr=sp[1])

    def save_pickle(self, file: str):
        with open(file, "wb") as f:
            pickle.dump(self, f)
        f.close()

    @classmethod
    def load_pickle(cls, file: str) -> "Cache":
        with open(file, "rb") as f:
            c: Cache = pickle.load(f)
        f.close()
        return c


def main() -> None:
    """
    Do a full scrap and print the results
    :return:
    """
    # Tuto funkci klidne muzes zmenit podle svych preferenci :)
    import json
    import time

    # === testing ===
    # URL = "https://python.iamroot.eu/"
    # cache = Cache(URL, "output")
    # cache.recursively_download_webpage()
    # cache.save()
    # cache.save_pickle("cache.obj")
    cache =  Cache.load_pickle("cache.obj")

    print(get_linux_only_availability(cache))  # WORKS
    # print(get_most_visited_webpage(cache))  # WORKS
    # find_secret_tea_party(cache)
    # print(get_changes(cache))  # TODO
    # print(get_most_params(cache))  # TODO

    # time_start = time.time()
    # print(json.dumps(scrap_all(cache).as_dict()))
    # print('took', int(time.time() - time_start), 's')


if __name__ == '__main__':
    main()
