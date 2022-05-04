import os, re, requests, pprint
from requests import Session
from typing import List
from utils import writeFolderToCBZ, statusBar

dictionary = {"+" : "", "!" : "", "?" : "", "%" : "", "*" : "", "/" : "", "#" : "", "\\": "", "&" : "and", ":" : "-",  '"' : ""}

class MangadexTitle:
    def __init__(self, link : str):
        self.link = link
        self.session = Session()
        self.id = self.getId()
        self.title = self.getTitle()
        self.chapters = self.getChapters()

    def getId(self) -> str:
        return re.search(r"/title/(.+?)/", self.link).group(1)
    
    def getTitle(self) -> str:
        infosApiLink = self.apiLink = "https://api.mangadex.org/manga/{id}"
        data = self.session.get(infosApiLink.format(id=self.id)).json()["data"]["attributes"]["title"]
        try :
            title = data["en"]
        except : 
            title = data[list(data)[-1]]
        return title.translate(str.maketrans(dictionary))
        

    def getChapters(self) -> List:
        chaptersApiLink = "https://api.mangadex.org/manga/{id}/feed?limit=500&translatedLanguage[]=en"
        res = self.session.get(chaptersApiLink.format(id=self.id)).json()
        data = res["data"]
        availableChapters = {}
        for element in data :
            if element["attributes"]["chapter"] == None : 
                availableChapters[0] = element["id"]
            else:
                chapter = float(element["attributes"]["chapter"])
                if int(chapter) == chapter :
                    availableChapters[int(chapter)] = element["id"]
                else:
                    availableChapters[chapter] = element["id"]
        return availableChapters

class MangadexChapter:
    def __init__(self, mangaTitle : str, id : str):
        self.session = Session()
        self.mangaTitle = mangaTitle
        self.id = id
        self.infos = self.getInfos()
        self.title = self.getTitle()
        self.chapter = self.getChapter()
        self.groups = self.getGroups()
        self.path = self.getPath()
        self.baseUrl, self.hash, self.pages = self.getPages()
    
    def getInfos(self):
        return self.session.get(f"https://api.mangadex.org/chapter/{self.id}").json()
    
    def getTitle(self) -> str:
        title = ''
        try : 
            title = self.infos["data"]["attributes"]["title"].translate(str.maketrans(dictionary))
        except :
            title = ''
        return title

    def getChapter(self):
        return self.infos["data"]["attributes"]["chapter"]
    
    def getGroups(self):
        groups = []

        for y in self.infos["data"]["relationships"]:
            if y["type"] == "scanlation_group" :
                groupId = y["id"]
                groupLink = f"https://api.mangadex.org/group/{groupId}"
                groupData = self.session.get(groupLink).json()
                groups.append(groupData["data"]["attributes"]["name"])

        groups = ' & '.join(groups).translate(str.maketrans(dictionary))

        return groups
    
    def getPath(self):
        path = f"Manga/{self.mangaTitle}/{self.mangaTitle} Ch. {self.chapter} - {self.title} (en) [{self.groups}]"
        if len(path)>200:
            path = path = f"Manga/{self.mangaTitle}/{self.mangaTitle} Ch. {self.chapter} - (en) [{self.groups}]"
        return path
    
    def getPages(self):
        pagesLink = f"https://api.mangadex.org/at-home/server/{self.id}"
        pagesData = self.session.get(pagesLink).json()

        baseUrl = pagesData["baseUrl"]
        pages = pagesData["chapter"]["data"]
        hash = pagesData["chapter"]["hash"]

        return baseUrl, hash, pages
    
    def download(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        print(f"downloading : {self.mangaTitle} Chapter {self.chapter}")

        for i,page in enumerate(self.pages) : 
            imageUrl = f"{self.baseUrl}/data/{self.hash}/{page}"
            ext = page.split('.')[-1]

            with open(f"{self.path}/page {str(i).zfill(3)}.{ext}", 'wb+') as img :                
                dt = self.session.get(imageUrl)
                img.write(dt.content)
            statusBar(len(self.pages),i+1)

        writeFolderToCBZ(self.path)

        print(f"downloaded : {self.mangaTitle} Chapter {self.chapter}")

# https://mangadex.org/title/53f25044-1d36-4966-89bc-4e1d259778f2/neko-ga-nishi-mukya
# https://mangadex.org/title/1003024d-101c-4fb6-86e6-033167bab723/amai-seikatsu
# https://mangadex.org/title/0149daa5-89c9-4e05-bf4f-f2440e0d2db7/kimi-no-koe

def main():
    Manga = MangadexTitle(input())

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
                lowerBound = requested.split('-')[0]
                upperBound = requested.split('-')[1]

                for chapter in Manga.chapters:
                    if float(lowerBound) <= chapter and chapter <= float(upperBound) :
                        chaptersToBeDownloaded[chapter] = Manga.chapters[chapter]

            else :
                if float(requested) in Manga.chapters:
                    chapter = int(requested) if int(requested) == float(requested) else float(requested)
                    chaptersToBeDownloaded[chapter] = Manga.chapters[chapter]
    
    for chapter in sorted(chaptersToBeDownloaded):
        chapter = MangadexChapter(Manga.title, chaptersToBeDownloaded[chapter])
        chapter.download()


if __name__ == '__main__':
    main()