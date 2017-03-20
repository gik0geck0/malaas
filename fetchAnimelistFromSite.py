#!/usr/bin/env python3

# Usage: $0 username
# Output: json list
# Side-effect: cache in mal_cache.db (Sqlite3)

import re
from mal_common import fetchPage
import sys
import json

def extractAnimeList(html):
    table = html.find("table")
    return table.attrs["data-items"]

def fetchAnimeList(username):
    fullList = []
    # fetch each status (in an attempt to get everything in single pages)
    for status in range(1,7):
        listHtml = fetchPage("/animelist/%s?status=%i" % (username, status))
        listStr = extractAnimeList(listHtml)
        listJson = json.loads(listStr)
        fullList.extend(listJson)
    return fullList

username = sys.argv[1]
animelist = fetchAnimeList(username)

from mal_db import loadAnimelist
loadAnimelist(username, animelist)

# print(json.dumps(animelist, ensure_ascii=False).encode('utf-8'))
