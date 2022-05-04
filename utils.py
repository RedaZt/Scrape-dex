import os, shutil, zipfile

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