
from common.mal_common import fetchAndCacheAnime
from common.mal_db import getUniqueAnimeIdsInLists

animeIds = list(getUniqueAnimeIdsInLists())
i=0
for anime_id in animeIds:
    fetchAndCacheAnime(anime_id[0])
    i+=1
    print("%i / %i" % (i, len(animeIds)))
