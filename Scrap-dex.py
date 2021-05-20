import sys, os, shutil, urllib3, json, zipfile, pprint

dictionary = {"+" : "", "!" : "", "?" : "", "%" : "", "*" : "", "/" : "", "#" : "", "\\": "", "&" : "and", ":" : "-",  '"' : ""}
http = urllib3.PoolManager()

def zipping(directory) :
    imgs = os.listdir(directory)
    with zipfile.ZipFile(directory+'.cbz', 'w') as targetfile :
        for img in imgs :
            targetfile.write(directory+'/'+img, img)

def statusBar(total,current):
    end = ''
    if total == current : end = '\n'
    width_of_bar = 50
    x = int((current / total)  * width_of_bar)
    printed_string = "".join([('█' if i < x else ' ') for i in range(width_of_bar)])
    out = "status : [" + printed_string + "] " + str(int((current / total) * 100)) + "%\r"
    print(f"{out}\r",end=end)

def chapterDownloader(id):
    link = f"https://api.mangadex.org/chapter/{id}"
    res = http.request('GET', link)
    data = json.loads(res.data.decode('utf8'))

    pages = data["data"]["attributes"]["data"]
    title = data["data"]["attributes"]["title"].translate(str.maketrans(dictionary))
    hash = data["data"]["attributes"]["hash"]
    chapter = data["data"]["attributes"]["chapter"]
    groups = []

    for y in data["relationships"]:
        if y["type"] == "scanlation_group" :
            group_id = y["id"]
            group_link = f"https://api.mangadex.org/group/{group_id}"
            res4 = http.request('GET', group_link)
            group_data = json.loads(res4.data.decode('utf8'))
            groups.append(group_data["data"]["attributes"]["name"])
    for y in data["relationships"]:
        if y["type"] == "manga" :
            manga_id = y["id"]
            manga_link = f"https://api.mangadex.org/manga/{manga_id}"
            res4 = http.request('GET', manga_link)
            manga_data = json.loads(res4.data.decode('utf8'))
            manga_title = manga_data["data"]["attributes"]["title"]["en"].translate(str.maketrans(dictionary))

    groups = ' & '.join(groups)

    directory = f"Manga/{manga_title}/{manga_title} Ch. {chapter} - {title} (en) [{groups}]"
    if not os.path.exists(directory):
        os.makedirs(directory)

    print(f"downloading : {manga_title} Chapter {chapter}")

    for i,page in enumerate(pages) : 
        request_link = f"https://api.mangadex.org/at-home/server/{id}"
        res3 = http.request('GET', request_link)
        server = json.loads(res3.data.decode('utf8'))["baseUrl"]
        base_link = f"{server}/data/{hash}/{page}"
        ext = page.split('.')[-1]
        with open(f"{directory}/page {str(i).zfill(3)}.{ext}", 'wb+') as img :                
            dt = http.request('GET', base_link)
            img.write(dt.data)
        statusBar(len(pages),i+1)
    zipping(directory)
    shutil.rmtree(directory)

    print(f"downloaded : {manga_title} Chapter {chapter}")


def titleDownloader(id) :
    # getting manga info
    link = f"https://api.mangadex.org/manga/{id}"
    res = http.request('GET', link)
    data = json.loads(res.data.decode('utf8'))

    manga_title = data["data"]["attributes"]["title"]["en"].translate(str.maketrans(dictionary))

    # getting available chapters
    feed_link = link = f"https://api.mangadex.org/manga/{id}/feed"
    res2 = http.request('GET', feed_link)
    data = json.loads(res2.data.decode('utf8'))
    chapters = data["results"]

    available_chapters = []
    for x in chapters :
        if x["data"]["attributes"]["translatedLanguage"] == "en" : 
            available_chapters.append(x["data"]["attributes"]["chapter"])
    print(f"Manga : {manga_title}")
    print("Available Chapter : ")
    print(sorted(map(int,available_chapters)))


    requested_chapters = input("Chapters you want to download : ")
    while requested_chapters == '' :
        requested_chapters = input("Chapters you want to download : ")
    if requested_chapters == '*':
        requested_chapters = available_chapters
    elif '-' in requested_chapters:
        requested_chapters = requested_chapters.split('-')
        l = []
        for x in available_chapters:
            if float(requested_chapters[0]) <= float(x) and float(x) <= float(requested_chapters[1]) :
                l.append(x)
        requested_chapters = l
    else :
        requested_chapters = requested_chapters.replace(' ','')
        requested_chapters = requested_chapters.split(',')
        for x in requested_chapters:
            if x not in available_chapters :
                del(requested_chapters[requested_chapters.index(x)])
    
    if '0' in requested_chapters :
        requested_chapters[requested_chapters.index('0')] = ''


    # pprint.pprint(chapters)
    chapters_to_download = []
    for x in requested_chapters:
        for chapter in chapters:
            if chapter["data"]["attributes"]["translatedLanguage"] == "en" and  chapter["data"]["attributes"]["chapter"] == x:
                chapters_to_download.append(chapter["data"]["id"])
    
    for id in chapters_to_download :
        chapterDownloader(id)


def mangaSearch(title) :
    # prepare the title
    title = '%'.join(title.split())
    link = f"https://api.mangadex.org/manga?title={title}"

    # getting search results
    res = http.request('GET', link)
    data = json.loads(res.data.decode('utf8'))
    
    results = {}
    for x in data["results"] : 
        results[x["data"]["attributes"]["title"]["en"]] = x["data"]["id"]

    # printing results
    results_keys = list(results.keys())
    for i,x in enumerate(results_keys) :
        print(f"{i+1}. {x}")
    
    manga_index = int(input("Enter the number of the manga you want to download : "))
    
    titleDownloader(results[results_keys[manga_index-1]])


if __name__ == "__main__" :

    # id="85a99758-de39-471e-9f6d-800547f53d0a"
    # link = f"https://api.mangadex.org/manga/{id}"
    # link = f"https://api.mangadex.org/chapter/{id}"
    # link = "https://api.mangadex.org/at-home/server/{id}"
    # link = "https://api.mangadex.org/manga?title="
    # https://{md@h server node}/data/{data.attributes.hash}/{data.attributes.data}

    # chapter example :
    # https://api.mangadex.org/chapter/8425f08f-dbcc-43b1-bb2e-a7a4d0842108

    title = input()
    mangaSearch(title)
