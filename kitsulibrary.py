"""
Contains functions and classes for extracting kitsu library information

Classes:
    Media

Functions:
    kitsu_library_gen(int, int, List[int], List[str]) -> List[Media]

Misc:
    These are filters for kitsu_library_gen:
        CURRENT

        PLANNED

        COMPLETED

        ONHOLD

        DROPPED

        ALL
"""
import requests
from typing import List

CURRENT = 0
PLANNED = 1
COMPLETED = 2
ONHOLD = 3
DROPPED = 4
ALL = 5

__filters = {
    CURRENT: "&filter%5Bstatus=current",
    PLANNED: "&filter%5Bstatus=planned",
    COMPLETED: "&filter%5Bstatus=completed",
    ONHOLD: "&filter%5Bstatus=on_hold",
    DROPPED: "&filter%5Bstatus=dropped",
    ALL: ""
}

class Media:
    """
    A class representing a kitsu library entry
    ------------------------------------------
    Attributes:
        canonicalTitle (str): title of show

        type (str): either anime or manga

        synopsis (str): show plot summary

        titles (dict): titles in various languages (ideally english, romanji, and japanese)

        poster (str): url for poster image

        kitsuUrl (str): url for kitsu entry
    """
    def __init__(self, data: dict) -> None:
        self.canonicalTitle: str = data['attributes']['canonicalTitle']
        self.type: str = data['type']
        self.synopsis: str = data['attributes']['synopsis']
        self.titles: dict = data['attributes']['titles']
        self.poster: str = data['attributes']['posterImage']['original']
        self.kitsuUrl: str = f"https://kitsu.io/anime/{data['attributes']['slug']}"

    def __str__(self) -> str:
        if self.type == "anime": return "Anime<" + self.canonicalTitle + ">"
        return "Manga<" + self.canonicalTitle + ">"
    
    def __repr__(self) -> str:
        return str(self)
        

def __get_user_library(userid: int, count: int = 10, offset: int = 0, contentfilter: int = 5, mtype: str = "anime") -> List[Media]:
    f = __filters[contentfilter]
    url = f"https://kitsu.io/api/edge/library-entries?fields[users]=id&filter[kind]={mtype}&filter[user_id]={userid}{f}&include={mtype},user&page[limit]={count}&page[offset]={offset}"
    response = requests.get(url, headers={"Accept":"application/vnd.api+json","Content-Type":"application/vnd.api+json"}).json()
    if response['data'] == []: return []
    fd = filter(lambda x: x['type'] == mtype, response['included'])
    return list(map(lambda x: Media(x), fd))

def kitsu_library_gen(userid: int, count: int = 10, filters: List[int] = [COMPLETED], mtype: List[str] = ["anime"]) -> List[Media]:
    """
    Generator that queries for a users library

            Parameters:
                userid  (int)      : kitsu's unique numeric id for the user. 
                                    Can be found in the user's url or in kitsu's GET requests
                count   (int)      : how many items to query for at a time

                filters (List[int]): which of the 5 progess categories to pull from

                mtype   (List[str]): either anime, manga, or both

            Returns:
                List of objects containing import info about library entries
    """
    offset = 0
    currentf = 0
    currentt = 0
    while True:
        if currentf == len(filters):
            currentf = 0
            currentt += 1
        if currentt == len(mtype):
            break
        x = __get_user_library(userid, count, offset, filters[currentf], mtype[currentt])
        if x == []:
            currentf += 1
            offset = 0
            continue
        yield x
        offset += count
    yield []

# Example use of library gen, using Ephin's id 1270113
# g = kitsu_library_gen(1270113,10,[CURRENT],["anime","manga"])
# x = None
# while x != []:
#     x = next(g)
#     print(x)
