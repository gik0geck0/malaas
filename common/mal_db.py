
import sqlite3
# db directory is relative to top-level (where binaries live)
db = sqlite3.connect("db/mal_cache.db")

def getCursor():
    return db.cursor()

def checkAnimeTable(c):
    malAnimeInfo = c.execute("pragma table_info('anime')").fetchall()
    if len(malAnimeInfo) is 0:
        # Create the table
        c.executescript("""create table anime (
            anime_id INTEGER PRIMARY KEY,
            title        VARCHAR(255),
            title_english VARCHAR(255),
            title_synonym VARCHAR(255)
        );
        CREATE TABLE joinAnimeGenre (
            anime_id INTEGER,
            genre_id INTEGER,
            UNIQUE (anime_id, genre_id) ON CONFLICT REPLACE
        );
        CREATE TABLE genre (
            genre_id INTEGER PRIMARY KEY,
            name VARCHAR(20)
        );""")

anime_list_columns = [
    # ( dbCol, dbType, malJsonKey=None )
    ("username", "VARCHAR(255)"),
    ("anime_id", "INTEGER"),
    ("my_score", "INTEGER", "score"),
    ("is_rewatching", "INTEGER"),
    ("status", "INTEGER"),
    ("storage_string", "VARCHAR(255)"),
    ("priority_string", "VARCHAR(255)"),
    ("num_watched_episodes", "INTEGER"),
    ("start_date_string", "VARCHAR(255)"),
    ("finish_date_string", "VARCHAR(255)")
]
def colDefToStr(colDef):
    return "%s %s" % (colDef[0], colDef[1])

def checkAnimelistTable(c):
    tableInfo = c.execute("pragma table_info('anime_list')").fetchall()
    if len(tableInfo) is 0:
        tableSql = ", ".join(map(colDefToStr, anime_list_columns))
        c.execute("""
        CREATE TABLE anime_list (%s,
            UNIQUE (anime_id, username) ON CONFLICT REPLACE
        )
        """ % tableSql)

def dbCheck():
    c = getCursor()
    checkAnimeTable(c)
    checkAnimelistTable(c)

    return True

# If you import mal_db, this will ensure that the DB has the right structure
dbCheck()

def getAnimelistByUsername(username, cursor=None):
    if cursor is None:
        cursor = getCursor()
    return cursor.execute("SELECT * FROM anime_list").fetchall()

def getUniqueAnimeIdsInLists():
    c = getCursor()
    return c.execute("SELECT anime_id FROM anime_list GROUP BY anime_id")

def mapAnimelistEntriesToTableValues(malJson, username):
    def jsonKeysFromColDef(colDef):
        return colDef[0] if len(colDef)==2 else colDef[2]
    def filterOutUsername(colName):
        return colName != "username"

    colNames = map(jsonKeysFromColDef,anime_list_columns)
    colNames = list(filter(filterOutUsername, colNames))
    tableValues = []
    for jsonObj in malJson:
        jsonVals = [username]
        for colName in colNames:
            jsonVals.append(jsonObj[colName])
        tableValues.append(tuple(jsonVals))
    return tableValues

def loadAnimelist(username, malJson):
    c = getCursor()
    # If there's already data, we need to update
    if len(getAnimelistByUsername(c)) > 0:
        # Update
        raise Exception("loadAnimelist#update is not supported")
    else:
        # Insert
        valueQuestions = ",".join(["?"]*len(anime_list_columns))
        colNames = ",".join([colDef[0] for colDef in anime_list_columns])
        sqlInsert = "INSERT INTO anime_list (%s) VALUES (%s)" % (colNames, valueQuestions)
        print(sqlInsert)
        values = mapAnimelistEntriesToTableValues(malJson, username)
        # for v in values:
        #     print(v)
        c.executemany(sqlInsert, values)
        c.connection.commit()
        print("done")
# TODO: Did it succeed?
