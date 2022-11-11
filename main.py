import os, re, shutil, zipfile
from time import sleep
from requests import get
from typing import List

specialCharacters = {
    '\\': '',
    '/': '',
    ':': '',
    '*': '',
    '?': '',
    '"': '',
    '<': '',
    '>': '',
    '|': ''
}
headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}


def writeFolderToCBZ(directory):
    images = os.listdir(directory)
    with zipfile.ZipFile(directory + '.cbz', 'w') as targetfile :
        for image in images :
            targetfile.write(f"{directory}/{image}", image)
    shutil.rmtree(directory)

def statusBar(total, current):
    end = ''
    if total == current : 
        end = '\n'
    width = 50
    x = int((current / total)  * width)
    printedString = "".join(['█' if i < x else ' ' for i in range(width)])
    out = f"Status : [{printedString}] {current}/{total}\r"
    print(f"{out}",end=end)

class MangadexTitle:
    def __init__(self, link : str):
        self.link = link
        self.id = self.getId()
        self.title = self.getTitle()
        self.chapters = self.getChapters()

    def getId(self) -> str:
        return re.search(r"/title/(.+?)/", self.link).group(1)

    def getTitle(self) -> str:
        infosApiLink = "https://api.mangadex.org/manga/{}"
        data = get(
            infosApiLink.format(self.id),
            headers=headers
        ).json()["data"]["attributes"]["title"]

        try :
            title = data["en"]
        except : 
            title = data[list(data)[-1]]
            
        return title.translate(str.maketrans(specialCharacters))

    def getChapters(self) -> List:
        chaptersApiLink = "https://api.mangadex.org/manga/{}/feed?limit=500&translatedLanguage[]=en"
        res = get(chaptersApiLink.format(self.id)).json()
        data = res["data"]
        availableChapters = {}

        for element in data :
            if element["attributes"]["chapter"] == None :
                chapter = 0
            else:
                chapter = float(element["attributes"]["chapter"])
                if int(chapter) == chapter:
                    chapter = int(chapter)
                # try:
                #     chapter = int(element["attributes"]["chapter"])
                # except:
                #     chapter = float(element["attributes"]["chapter"])

            if chapter in availableChapters:
                availableChapters[chapter].append(element["id"])
            else:
                availableChapters[chapter] = [element["id"]]

        return availableChapters

class MangadexChapter:
    def __init__(self, mangaTitle : str, id : str):
        self.mangaTitle = mangaTitle
        self.id = id
        self.infos = self.getInfos()
        self.chapter = self.getChapter()

    def getInfos(self):
        return get(f"https://api.mangadex.org/chapter/{self.id}", headers=headers).json()
    
    def getTitle(self) -> str:
        try : 
            title = self.infos["data"]["attributes"]["title"].translate(str.maketrans(specialCharacters))
        except :
            title = ''
            
        return title

    def getChapter(self):
        return self.infos["data"]["attributes"]["chapter"] or '0'

    def getGroups(self):
        groups = []
        for x in self.infos["data"]["relationships"]:
            if x["type"] == "scanlation_group" :
                groupId = x["id"]
                groupApiLink = "https://api.mangadex.org/group/{}"
                groupData = get(groupApiLink.format(groupId)).json()
                groups.append(groupData["data"]["attributes"]["name"])
        groups = ' & '.join(groups).translate(str.maketrans(specialCharacters))
        return groups or "No Group"
    
    def getPath(self):
        title = self.getTitle()
        groups = self.getGroups()

        path = f"Manga/{self.mangaTitle}/{self.mangaTitle} Ch. {self.chapter} - {title} (en) [{groups}]"
        if len(path)>200:
            path = f"Manga/{self.mangaTitle}/{self.mangaTitle} Ch. {self.chapter} - (en) [{groups}]"
        return path
    
    def getPages(self):
        pagesApiLink = "https://api.mangadex.org/at-home/server/{}"
        pagesData = get(pagesApiLink.format(self.id)).json()
        
        baseUrl = pagesData["baseUrl"]
        pages = pagesData["chapter"]["data"]
        hash = pagesData["chapter"]["hash"]

        return baseUrl, hash, pages
    
    def download(self):
        baseUrl, hash, pages = self.getPages()
        numberOfPages = len(pages)
        path = self.getPath()

        if not os.path.exists(path):
            os.makedirs(path)

        print(f"Downloading : {self.mangaTitle} Chapter {self.chapter}")

        for i,page in enumerate(pages) : 
            imageUrl = f"{baseUrl}/data/{hash}/{page}"
            ext = page.split('.')[-1]

            with open(f"{path}/page {str(i).zfill(3)}.{ext}", 'wb+') as img :                
                dt = get(imageUrl)
                img.write(dt.content)
            statusBar(numberOfPages,i+1)

        writeFolderToCBZ(path)

def main():
    Manga = MangadexTitle(input("Paste series link here : ") + '/')

    print(f"Manga : {Manga.title}")
    print(f"Available Chapters :\n{sorted(Manga.chapters)}")

    requestedChapters = ''
    while requestedChapters == '' :
        requestedChapters = input("Chapters you want to download : ")

    if requestedChapters == '*':
        chaptersToBeDownloaded = Manga.chapters
    else: 
        requestedChapters = [s.strip() for s in requestedChapters.split(',')]
        chaptersToBeDownloaded = {}
        
        for requested in requestedChapters:
            if '-' in requested:
                lowerBound, upperBound = map(float, requested.split('-'))
                for chapter in Manga.chapters:
                    if lowerBound <= chapter  <= upperBound:
                        chaptersToBeDownloaded[chapter] = Manga.chapters[chapter]
            else :
                chapter = float(requested)
                if chapter in Manga.chapters:
                    chaptersToBeDownloaded[chapter] = Manga.chapters[chapter]
    
    for requested in sorted(chaptersToBeDownloaded):
        for chapter in chaptersToBeDownloaded[requested]:
            MangadexChapter(Manga.title, chapter).download()
    
    print("ALL DONE !!")

if __name__ == '__main__':
    main()