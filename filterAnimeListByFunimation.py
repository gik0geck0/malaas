#!/usr/bin/env python2
# stdin: list of anime titles, one per line
# stdout: subset of that list that are available on crunchyroll

import sys
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlencode

def fetchSearchPage(title):
    fullUrl = "https://www.funimation.com/search?%s" % urlencode({"q": title})
    response = urlopen(fullUrl)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    return soup

def hrefToFuniLink(href):
    return "https://www.funimation.com%s" % href

def searchByTitle(malTitle):
    funiHtml = fetchSearchPage(malTitle)
    searchResults = funiHtml.find_all("a", class_="show-title")

    if len(searchResults) > 0:
        print("%s (%s)" % (malTitle, hrefToFuniLink(searchResults[0].attrs["href"])))
    else:
        print("%s could not be found on funimation" % malTitle)

for malTitle in sys.stdin.readlines():
    malTitle = malTitle.strip()
    searchByTitle(malTitle)
