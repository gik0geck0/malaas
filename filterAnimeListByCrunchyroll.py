#!/usr/bin/env python2
# stdin: list of anime titles, one per line
# stdout: subset of that list that are available on crunchyroll

from crunchyroll.apis.meta import MetaApi as CRMetaApi
import sys

crApi = CRMetaApi()

for malTitle in sys.stdin.readlines():
    malTitle = malTitle.strip()
    searchResults = crApi.search_anime_series(malTitle)
    if len(searchResults) == 0:
        # print("MAL Title %s had no results on crunchyroll" % malTitle)
        pass
    else:
        print("%s (%s)" % (malTitle, searchResults[0].name))
        # print("Full results:", searchResults)
