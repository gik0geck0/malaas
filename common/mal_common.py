
from bs4 import BeautifulSoup
from urllib.request import urlopen

# Relative Path off mal domain
# e.g. "/anime/31646"
def fetchPage(path):
    """
    Retrieves and parses a page from myanimelist
    @param path Absolute path off mal domain. E.g. "/anime/31646"
    @return BeautifulSoup-parsed page
    """
    fullUrl = "https://myanimelist.net%s" % path
    response = urlopen(fullUrl)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    return soup

import re
import sys
from common.mal_db import getCursor

def genreIsInCache(genreId):
    c = getCursor()
    return 1 == len(c.execute("select genreId from genre where genreId=:genreId", {"genreId":genreId}).fetchall())

def ensureGenreInCache(genreId, name):
    if not genreIsInCache(genreId):
        # Add this genre
        c = getCursor()
        res = c.execute("insert into genre VALUES (?, ?);", (genreId, name))
        c.connection.commit()

def extractAnimeGenresFromPage(animeHtml):
    return animeHtml.find(
               "span",
               class_="dark_text",
               string="Genres:"
           ).parent.find_all("a")

def extractGenreFromLink(anchor):
    """
    @param anchor Anchor tag representing the link to the genre
    @return (genreId, name)
    """
    # matches /anime/genre/{genreId}/{genreName}
    matchObj = re.search("/anime/genre/([0-9]+)/(\w+)", anchor.attrs["href"])
    return (matchObj.group(1), matchObj.group(2))


def animeIsInCache(animeId):
    isCached = 1 == len(
            getCursor().execute(
                "select animeId from anime where animeId=:animeId;",
                { "animeId": animeId }
            )
            .fetchall())
    return isCached

def ensureAnimeInCache(animeId, title, titleEnglish, titleSynonym):
    if not animeIsInCache(animeId):
        c = getCursor()
        c.execute("insert into anime (animeId, title, titleEnglish, titleSynonym) VALUES (?, ?, ?, ?);",
                (animeId, title, titleEnglish, titleSynonym))
        c.connection.commit()

def extractAnimeInfoFromPage(animeHtml):
    mainTitle = animeHtml.title.string.replace(' - MyAnimeList.net', '').strip()
    altTitles = animeHtml.find('h2', string="Alternative Titles")
    englishTitle = ""
    synonymTitle = ""
    if altTitles.parent.find('span', string="English:") is not None:
        englishTitle = list(altTitles.parent.find('span', string="English:").parent.strings)[2].strip()
    if altTitles.parent.find('span', string="Synonyms:") is not None:
        synonymTitle = list(altTitles.parent.find('span', string="Synonyms:").parent.strings)[2].strip()
    asTuple = (mainTitle, englishTitle, synonymTitle)
    return asTuple

def joinAnimeToGenre(animeId, genreId):
    c = getCursor()
    c.execute("""insert into joinAnimeGenre (animeId, genreId) VALUES (?,?);""",
              (animeId, genreId))
    c.connection.commit()

def fetchAndCacheAnime(animeId, force=False):
    """Side effect: This anime's info is cached in the DB"""

    if force or not animeIsInCache(animeId):
        # Fetch this anime's page
        animeHtml = fetchPage("/anime/%s" % animeId)

        # Pull out and cache the genres
        genreLinkList = extractAnimeGenresFromPage(animeHtml)
        genres = [extractGenreFromLink(genreTag) for genreTag in genreLinkList]
        for genre in genres:
            ensureGenreInCache(*genre)

        # Make sure the anime is cached
        ensureAnimeInCache(animeId, *extractAnimeInfoFromPage(animeHtml))
        
        # Link anime to genres
        for genre in genres:
            joinAnimeToGenre(animeId, genre[0])
