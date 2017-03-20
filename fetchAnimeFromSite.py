#!/usr/bin/env python3

# Usage: $0 <animeId>
# Output: Key: Value for all "known" information
# Side-effect: cache in mal_cache.db (Sqlite3)


from lib.mal_common import fetchAndCacheAnime
fetchAndCacheAnime(sys.argv[1])
