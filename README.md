# Scrap-dex
Python script to download manga from [MangaDex.org](https://mangadex.org/).
Search and download based script, written using MangaDex API v5.

## Requirements
  * [Python 3.4+](https://www.python.org/downloads/)
  * requests

## Usage
  * Download the source code.
  * Run the "main.py" file.

### Example usage
```
Search : ranger reject
1. Ranger Reject
Enter the number of the manga you want to download : 1
Manga : Ranger Reject
Available Chapters : 
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
Chapters you want to download : 1-5,8, 20-26

Downloading : Ranger Reject Chapter 1
status : [██████████████████████████████████████████████████] 100%

... (and so on)
```

### Current limitations
  * The script will download all available releases of each chapter specified.