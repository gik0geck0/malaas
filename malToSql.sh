#!/bin/bash
# Usage:
#   $1: mal.xml
#   stdout: sqllite DML

inputXml="$1"

function regexTest {
    regex=$1
    input=$2
    echo "$input" | grep -E ".*$regex.*" | wc -l
}

# Create Table using tags in the first <anime>
echo "
DROP TABLE IF EXISTS animeList;
CREATE TABLE animeList (
    sqlAnimeId INTEGER PRIMARY KEY AUTOINCREMENT"

columns=$(xmllint "$inputXml" --xpath '/myanimelist/anime[1]' | sed -r 's/\s*<(|\/?anime>)//' | sed -r 's/\/?>.*//')
for colName in $columns; do
    type="VARCHAR(255)"
    isNumber=$(regexTest 'episodes|score|_id|times|rewatching_ep' colName)
    if [ "$isNumber" == "1" ]; then
        type="INTEGER"
    fi
    echo "    , $colName $type"
done

echo ");"

echo "INSERT INTO animeList("
first=1
for colName in $columns; do
    if [ $first != 1 ]; then
        echo -n ", "
    else 
        first=0
    fi
    echo "$colName"
done
echo ") VALUES"

# Create an insert command per <anime>
numAnime=$(xmllint "$inputXml" --xpath '/myanimelist/myinfo/user_total_anime/text()')
for i in $(seq $numAnime); do
    if [ $i != 1 ]; then
        echo ",("
    else
        echo "("
    fi

    animeXml=$(xmllint "$inputXml" --nocdata --xpath "/myanimelist/anime[$i]")
    first=1
    for colName in $columns; do
        if [ $first != 1 ]; then
            echo -n ", "
        else
            first=0
        fi
        value=$(echo "$animeXml" | grep "<$colName>" | sed -r 's/\s*<[a-z_]+>//' | sed -r 's/<\/[a-z_]+>$//')
        if [ $(regexTest '^[0-9]+$' "$value") == 1 ]; then
            echo "    $value"
        else
            echo "    '$value'"
        fi
    done
    echo ")"
done
echo ";"
