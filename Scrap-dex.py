import sys, os, requests, json, zipfile, urllib3
from time import sleep

http = urllib3.PoolManager()

dictio = { "+" : "", "!" : "", "?" : "", "%" : "", "*" : "", "/" : "", "#" : "", "#" : "", "\\": "", "&" : "and", ":" : "-", }

def zipping(manga_title, chapter_folder) :
    os.chdir("C:/Users/moroc/Documents/Projects/Python/downloads/"+manga_title)
    imgs = os.listdir(chapter_folder)
    with zipfile.ZipFile(chapter_folder+'.cbz', 'w') as targetfile :
        os.chdir(chapter_folder)
        for index, file in enumerate(imgs) :
            targetfile.write(file)
    os.chdir("C:/Users/moroc/Documents/Projects/Python/downloads/"+manga_title)

    
def status_bar(total,current):
    width_of_bar = 50
    x = int((current / total)  * width_of_bar)
    printed_string = "".join([('█' if i < x else ' ') for i in range(width_of_bar)])
    out = "status : [" + printed_string + "] " + str(int((current / total) * 100)) + "%\r"
    sys.stdout.write(out)
    sys.stdout.flush()

    
def downloader(manga_id):
    #getting manga info
    link = "https://mangadex.org/api/manga/"+manga_id
    R = requests.get(link)
    data = json.loads(R.text)
    manga_title = data['manga']['title']
    chapters_ids = data["chapter"]
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    os.chdir("downloads")

    #finding and printing available chapters
    available_chapters = []
    for id in chapters_ids:
        if chapters_ids[id]["lang_code"] == "gb" :
            if chapters_ids[id]["chapter"] == '':
                available_chapters.append(0)    
            else : 
                available_chapters.append(chapters_ids[id]["chapter"])  
    available_chapters.reverse() 
    print(available_chapters)

    #prepare the list for the requested chapters
    requested_chapters = input("Chapters you want to download : ")
    while requested_chapters == '' :
        requested_chapters = input("Chapters you want to download : ")
    if '-' in requested_chapters:
        requested_chapters = requested_chapters.split('-')
        l = []
        for x in available_chapters:
            if float(requested_chapters[0]) <= float(x) and float(x) <= float(requested_chapters[1]) :
                l.append(x)
        requested_chapters = l
    else :
        requested_chapters = requested_chapters.replace(' ','')
        requested_chapters = requested_chapters.split(',')

    chapters_to_download = []
    for x in requested_chapters:
        for id in chapters_ids:
            if chapters_ids[id]["lang_code"] == "gb" and  chapters_ids[id]["chapter"] == str(x):
                chapters_to_download.append(id)
    
    if not os.path.exists(manga_title):
        os.makedirs(manga_title)
    os.chdir(manga_title)

    #downloading
    for x in chapters_to_download :
        #getting chapter's infos
        chapters_title = chapters_ids[x]["title"].translate(str.maketrans(dictio))
        chapters_number = chapters_ids[x]["chapter"]
        group_name = chapters_ids[x]["group_name"]
        chapters_folder = manga_title+" Ch. "+chapters_number+" - "+chapters_title+" ["+group_name+']'
        
        #preparing chapter's folder
        if os.path.exists(chapters_folder):
                print(chapters_folder,"is already downloaded")
                break
        else:
                os.makedirs(chapters_folder)
        os.chdir(chapters_folder)  

        #chapter's link
        ch_link = "https://mangadex.org/api/chapter/"+x 

        # downloading the pages
        print("downloading",manga_title,"Chapter",chapters_ids[x]["chapter"])
        r = requests.get(ch_link)
        ch_data = json.loads(r.text)
        server = ch_data["server"]
        hash = ch_data["hash"]
        images = ch_data["page_array"]
        total = len(images)
        downloaded = 0
        for image in images:
            page_link = server+hash+'/'+image
            if os.path.exists(image):
                os.remove(image)
            with open(image, 'wb') as img :                
                dt = http.request('GET', page_link)
                img.write(dt.data)
            downloaded += 1
            status_bar(total,downloaded)
            sleep(1)
        print("\ndownloaded",manga_title,"Chapter",chapters_ids[x]["chapter"])
        
        zipping(manga_title, chapters_folder)


if __name__ == "__main__" :
    manga_url = input("link : ")
    manga_id = ''
    while "mangadex" and "title" not in manga_url :
        manga_url = input("Enter a valid link : ")
    segments = manga_url.split('/')
    for x in segments:
        if x.isnumeric() and len(x)>1 :
            manga_id = x
    if manga_id != '': 
        downloader(manga_id)
        print("All Done !!")
    else :
        print("Could not find title's id.")
