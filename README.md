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
Paste series link here : https://mangadex.org/title/87ebd557-8394-4f16-8afe-a8644e555ddc/hirayasumi
Manga : Hirayasumi
Available Chapters :
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
Chapters you want to download : 1-5,8,20-26

Downloading : Hirayasumi Chapter 1
Status : [██████████████████████████████████████████████████] 42/42

... (and so on)
```

### Current limitations
  * The script will download all available releases of each chapter specified.