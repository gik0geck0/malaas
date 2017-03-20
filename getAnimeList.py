
from common.mal_db import getCursor

print(getCursor().execute("SELECT * FROM anime_list").fetchall())
