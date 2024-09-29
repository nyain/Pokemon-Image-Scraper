# Pokémon Image Scraper

A Python-based scraper for collecting Pokémon images from **Bulbapedia** and **Bing Image Search**.

## Features
- Scrapes high-quality Pokémon images from Bulbapedia.
- Automatically fills missing images using Bing Image Search.
- Customizable Pokémon exclusions via a text file.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/nyain/Pokemon-Image-Scraper.git
    ```
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. **Exclusion List**: Add any Pokémon names to `filtered_pokemon_names.txt` to exclude them from scraping.
2. **Run the Scraper**:
    ```bash
    python ImageScrapper.py
    ```
   - Images will be saved in the `Training` folder, organized by Pokémon name.
   
## Notes
- **Dependencies**: Make sure to have `aiohttp`, `beautifulsoup4`, and `bing_image_downloader` installed.
- The scraper first tries Bulbapedia for images, then uses Bing if needed.
- For Windows, the event loop policy is set to avoid concurrency issues.
