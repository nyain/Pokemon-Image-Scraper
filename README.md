# Pokémon Image Scraper

A Python-based scraper that collects Pokémon images from **Bulbapedia** and **Bing Image Search** using **PokeAPI** to fetch all available Pokémon names.

## Features
- Scrapes high-quality Pokémon images from Bulbapedia.
- Fills missing images using Bing Image Search.
- Fetches all Pokémon names from **PokeAPI**.
- Supports customizable Pokémon exclusions via a text file.

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
1. **Exclusion List**: Add Pokémon names (in lowercase) to `filtered_pokemon_names.txt` to exclude them from being scraped.
2. **Run the Scraper**:
    ```bash
    py ImageScrapper.py
    ```
   - Pokémon names are fetched from **PokeAPI**.
   - Images are saved in the `Training` folder, organized by Pokémon name.
   
## Notes
- **Dependencies**: Ensure `aiohttp`, `beautifulsoup4`, `bing_image_downloader`, and other libraries in `requirements.txt` are installed.
- **Flow**: The scraper first attempts to download images from Bulbapedia. If fewer than 20 images are found, it uses Bing to fill in the rest.
- On **Windows**, the event loop policy is adjusted to avoid concurrency issues.
