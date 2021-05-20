import os, shutil, urllib3, json, zipfile, pprint

dictionary = {"+" : "", "!" : "", "?" : "", "%" : "", "*" : "", "/" : "", "#" : "", "\\": "", "&" : "and", ":" : "-",  '"' : ""}
http = urllib3.PoolManager()

def zipping(directory) :
    imgs = os.listdir(directory)
    with zipfile.ZipFile(directory+'.cbz', 'w') as targetfile :
        for img in imgs :
            targetfile.write(directory+'/'+img, img)

def titleDownloader(id) :
    link = f"https://api.mangadex.org/manga/{id}"
    res = http.request('GET', link)
    data = json.loads(res.data.decode('utf8'))

    manga_title = data["data"]["attributes"]["title"]["en"].translate(str.maketrans(dictionary))

    feed_link = link = f"https://api.mangadex.org/manga/{id}/feed"
    res2 = http.request('GET', feed_link)
    data = json.loads(res2.data.decode('utf8'))

    available_chapters = []
    for x in data["results"] :
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
    
    print(requested_chapters)


def mangaSearch(title) :
    title = '%'.join(title.split())
    link = f"https://api.mangadex.org/manga?title={title}"
    res = http.request('GET', link)
    data = json.loads(res.data.decode('utf8'))
    
    results = {}
    for x in data["results"] : 
        results[x["data"]["attributes"]["title"]["en"]] = x["data"]["id"]

    results_keys = list(results.keys())

    for i,x in enumerate(results_keys) :
        print(f"{i+1}. {x}")
    
    manga_index = int(input("Enter the number of the manga you want to download : "))
    
    titleDownloader(results[results_keys[manga_index-1]])


if __name__ == "__main__" :

    id="85a99758-de39-471e-9f6d-800547f53d0a"
    # id="7fd01936-334d-41a9-bf3e-2388aa7e514f"
    # link = f"https://api.mangadex.org/manga/8ae4d0f6-152a-4956-8664-4405758d26ae"
    # link = f"https://api.mangadex.org/chapter?manga=8ae4d0f6-152a-4956-8664-4405758d26ae"
    # link = f"https://api.mangadex.org/chapter/2fdd80e9-b64e-4022-8851-8fed1c3621d0"
    # link = "https://api.mangadex.org/at-home/server/2fdd80e9-b64e-4022-8851-8fed1c3621d0"
    # link = "https://api.mangadex.org/manga?title="
    # link = f"https://api.mangadex.org/manga/{id}"
    # https://{md@h server node}/data/{data.attributes.hash}/{data.attributes.data}

    title = input()
    mangaSearch(title)
    exit()
    res = http.request('GET', link)
    data = json.loads(res.data.decode('utf8'))

    pprint.pprint(data)
    exit()
    manga_title = data["data"]["attributes"]["title"]["en"].translate(str.maketrans(dictionary))
    directory = f"Manga/{manga_title}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    link = f"https://api.mangadex.org/manga/{id}/feed"
    res2 = http.request('GET', link)
    data = json.loads(res2.data.decode('utf8'))

    for x in data["results"] :
        if x["data"]["attributes"]["translatedLanguage"] == "en" : 
            pages = x["data"]["attributes"]["data"]
            id = x["data"]["id"]
            title = x["data"]["attributes"]["title"].translate(str.maketrans(dictionary))
            hash = x["data"]["attributes"]["hash"]
            chapter = x["data"]["attributes"]["chapter"]
            groups = []

            for y in x["relationships"]:
                if y["type"] == "scanlation_group" :
                    group_id = y["id"]
                    group_link = f"https://api.mangadex.org/group/{group_id}"
                    res4 = http.request('GET', group_link)
                    group_data = json.loads(res4.data.decode('utf8'))
                    groups.append(group_data["data"]["attributes"]["name"])

            groups = ' & '.join(groups)

            directory = f"Manga/{manga_title}/{manga_title} Ch. {chapter} - {title} (en) [{groups}]"
            if not os.path.exists(directory):
                os.makedirs(directory)

            for i,page in enumerate(pages) : 
                request_link = f"https://api.mangadex.org/at-home/server/{id}"
                res3 = http.request('GET', request_link)
                server = json.loads(res3.data.decode('utf8'))["baseUrl"]
                base_link = f"{server}/data/{hash}/{page}"
                # print(base_link)
                ext = page.split('.')[-1]
                with open(f"{directory}/page {str(i).zfill(3)}.{ext}", 'wb+') as img :                
                    dt = http.request('GET', base_link)
                    img.write(dt.data)
            zipping(directory)
            shutil.rmtree(directory)
    # pprint.pprint(data)
