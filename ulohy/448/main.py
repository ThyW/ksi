#!/usr/bin/env python3

import requests
import bs4

URL = "https://python.iamroot.eu/"


def task1() -> None:
    session = requests.Session()
    get_request = session.get(URL)
    page_html = get_request.content
    soup = bs4.BeautifulSoup(page_html, "html.parser")

    img = soup.find("img")
    print(img.get("src"))


def task2() -> None:
    session = requests.Session()
    get_request = session.get(URL + "extending/index.html")
    page_html = get_request.content
    soup = bs4.BeautifulSoup(page_html, "html.parser")

    first_page_links = soup.find_all("a")
    c1 = len([x for x in first_page_links
              if len(x.get("href")) >= 30])

    get_request = session.get(URL + "installing/index.html")
    page_html = get_request.content
    soup2 = bs4.BeautifulSoup(page_html, "html.parser")

    second_page_links = soup2.find_all("a")
    c2 = len([x for x in second_page_links if 
              len(x.get("href")) >= 30])

    print(c1 + c2)


def task3() -> None:
    session = requests.Session()
    get_request = session.get(URL + "tutorial/index.html")
    page_html = get_request.content
    soup = bs4.BeautifulSoup(page_html, "html.parser")

    paragraphs = soup.find_all("p")

    ff = paragraphs[0:4]
    text = "".join([x.text for x in ff])
    count = 0
    for each in text.split():
        if each.startswith("a") or each.startswith("A"):
            count += 1
        else:
            continue
    print(count)


def main():
    task1()
    task2()
    task3()


if __name__ == '__main__':
    main()
