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

def writeFolderToCBZ(directory):
    images = os.listdir(directory)
    with zipfile.ZipFile(directory + '.cbz', 'w') as targetfile :
        for image in images :
            targetfile.write(directory + '/' + image, image)
    shutil.rmtree(directory)

def statusBar(total, current):
    end = ''
    if total == current : end = '\n'
    width = 50
    x = int((current / total)  * width)
    printedString = "".join([('█' if i < x else ' ') for i in range(width)])
    out = f"status : [{printedString}] {current}/{total}\r"
    print(f"{out}\r",end=end)

class MangadexTitle:
    def __init__(self, link : str):
        self.link = link
        self.id = self.getId()
        self.title = self.getTitle()
        self.chapters = self.getChapters()

    def getId(self) -> str:
        return re.search(r"/title/(.+?)/", self.link).group(1)

    def getTitle(self) -> str:
        infosApiLink = self.apiLink = "https://api.mangadex.org/manga/{id}"
        data = get(infosApiLink.format(id=self.id), headers={"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}).json()["data"]["attributes"]["title"]
        try :
            title = data["en"]
        except : 
            title = data[list(data)[-1]]
        return title.translate(str.maketrans(specialCharacters))

    def getChapters(self) -> List:
        chaptersApiLink = f"https://api.mangadex.org/manga/{self.id}/feed?limit=500&translatedLanguage[]=en"
        res = get(chaptersApiLink).json()
        data = res["data"]
        availableChapters = {}
        for element in data :
            if element["attributes"]["chapter"] == None : 
                availableChapters[0] = element["id"]
            else:
                chapter = float(element["attributes"]["chapter"])
                if int(chapter) == chapter :
                    if int(chapter) in availableChapters:
                        availableChapters[int(chapter)] += [element["id"]]
                    else:
                        availableChapters[int(chapter)] = [element["id"]]
                else:
                    if chapter in availableChapters:
                        availableChapters[chapter] += [element["id"]]
                    else:
                        availableChapters[chapter] = [element["id"]]
        return availableChapters

class MangadexChapter:
    def __init__(self, mangaTitle : str, id : str):
        self.mangaTitle = mangaTitle
        self.id = id
        self.infos = self.getInfos()
        self.chapter = self.getChapter()
        self.baseUrl, self.hash, self.pages = self.getPages()

    def getInfos(self):
        return get(f"https://api.mangadex.org/chapter/{self.id}", headers={"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}).json()
    
    def getTitle(self) -> str:
        title = ''
        try : 
            title = self.infos["data"]["attributes"]["title"].translate(str.maketrans(specialCharacters))
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
                groupData = get(groupLink).json()
                groups.append(groupData["data"]["attributes"]["name"])

        groups = ' & '.join(groups).translate(str.maketrans(specialCharacters))

        return groups or "No Group"
    
    def getPath(self):
        title = self.getTitle()
        groups = self.getGroups()

        path = f"Manga/{self.mangaTitle}/{self.mangaTitle} Ch. {self.chapter} - {title} (en) [{groups}]"
        if len(path)>200:
            path = path = f"Manga/{self.mangaTitle}/{self.mangaTitle} Ch. {self.chapter} - (en) [{groups}]"
        return path
    
    def getPages(self):
        pagesLink = f"https://api.mangadex.org/at-home/server/{self.id}"
        pagesData = get(pagesLink).json()

        baseUrl = pagesData["baseUrl"]
        pages = pagesData["chapter"]["data"]
        hash = pagesData["chapter"]["hash"]

        return baseUrl, hash, pages
    
    def download(self):
        path = self.getPath()

        if not os.path.exists(path):
            os.makedirs(path)

        print(f"downloading : {self.mangaTitle} Chapter {self.chapter}")

        for i,page in enumerate(self.pages) : 
            imageUrl = f"{self.baseUrl}/data/{self.hash}/{page}"
            ext = page.split('.')[-1]

            with open(f"{path}/page {str(i).zfill(3)}.{ext}", 'wb+') as img :                
                dt = get(imageUrl)
                img.write(dt.content)
            statusBar(len(self.pages),i+1)

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
                lowerBound = requested.split('-')[0]
                upperBound = requested.split('-')[1]

                for chapter in Manga.chapters:
                    if float(lowerBound) <= chapter and chapter <= float(upperBound) :
                        chaptersToBeDownloaded[chapter] = Manga.chapters[chapter]
            else :
                chapter = float(requested)
                if chapter in Manga.chapters:
                    if int(chapter) == chapter:
                        chapter = int(chapter)

                    chaptersToBeDownloaded[chapter] = Manga.chapters[chapter]
    
    for requested in sorted(chaptersToBeDownloaded):
        for chapter in chaptersToBeDownloaded[requested]:
            MangadexChapter(Manga.title, chapter).download()
    
    print("ALL DONE !!")

if __name__ == '__main__':
    main()