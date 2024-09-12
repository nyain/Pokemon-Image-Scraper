# Pokémon Image Scraper

This repository contains a Python script that scrapes Pokémon images from [Bulbapedia](https://bulbapedia.bulbagarden.net) using asynchronous requests and BeautifulSoup. The script downloads images for all Pokémon listed in the [PokéAPI](https://pokeapi.co), organizing them into folders based on their names.

### Features:
- **Asynchronous scraping**: Utilizes `aiohttp` and `asyncio` to scrape and download images efficiently.
- **BeautifulSoup for parsing**: Extracts image URLs from Bulbapedia pages.
- **Folder management**: Creates separate folders for each Pokémon, storing up to 25 images per folder.
- **Concurrency control**: Limits the number of simultaneous requests to avoid overloading the server.

### How It Works:
1. Fetches a list of all Pokémon names from PokéAPI.
2. Scrapes image URLs from each Pokémon's Bulbapedia archive page.
3. Downloads and saves the images to corresponding folders.

### Requirements:
- `aiohttp`
- `requests`
- `beautifulsoup4`

### Usage:
1. Clone the repository.
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the script:
   ```
   python ImageScrapper.py
   ```

### Credits:
This project is based on a modified version of the [Pokémon repository](https://github.com/HybridShivam/Pokemon/tree/master) by HybridShivam. I adapted the original script to fit specific scraping needs for Bulbapedia. Special thanks to the original author for their work!
