import requests

filters = {
    "Currently Watching": "&filter%5Bstatus=current",
    "Want to Watch": "&filter%5Bstatus=planned",
    "Completed": "&filter%5Bstatus=completed",
    "On Hold": "&filter%5Bstatus=on_hold",
    "Dropped": "&filter%5Bstatus=dropped",
    "NONE": ""
}

def get_user_library(userid: int, count: int = 10, offset: int = 0, contentfilter: str = "NONE") -> list:
    f = filters[contentfilter]
    url = f"https://kitsu.io/api/edge/library-entries?fields[users]=id&filter[kind]=anime&filter[user_id]={userid}{f}&include=anime,user&page[limit]={count}&page[offset]={offset}"
    response = requests.get(url, headers={"Accept":"application/vnd.api+json","Content-Type":"application/vnd.api+json"}).json()
    if response['data'] == []: return []
    fd = filter(lambda x: x['type'] == 'anime', response['included'])
    return list(map(lambda x: x['attributes']['canonicalTitle'], fd))

def gen(userid: int, count: int = 10, filters: list = ["Completed"]) -> list:
    offset = 0
    currentf = 0
    while True:
        if currentf == len(filters):
            break
        x = get_user_library(userid, count, offset, filters[currentf])
        if x == []:
            currentf += 1
            offset = 0
            continue
        yield x
        offset += count
    yield []

g = gen(1270113,10,["Currently Watching"])
x = None
while x != []:
    x = next(g)
    print(x)
