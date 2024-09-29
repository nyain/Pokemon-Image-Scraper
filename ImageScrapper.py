import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from bing_image_downloader import downloader
import os
import re

# Dictionary for name mapping between PokeAPI and Bulbapedia
NAME_MAPPING = {
    'nidoran-m': 'Nidoran♂',
    'nidoran-f': 'Nidoran♀',
    'farfetchd': "Farfetch'd",
    'sirfetchd': "Sirfetch'd",
    'mr-mime': "Mr._Mime",
    'mr-rime': "Mr._Rime",
    'mime-jr': "Mime_Jr.",
    'ho-oh': "Ho-Oh",
    'porygon-z': "Porygon-Z",
    'ting-lu': "Ting-Lu",
    'chien-pao': "Chien-Pao",
    'wo-chien': "Wo-Chien",
    'chi-yu': "Chi-Yu",
    'type-null': "Type:_Null",
    'jangmo-o': "Jangmo-o",
    'hakamo-o': "Hakamo-o",
    'kommo-o': "Kommo-o",
    'tapu-koko': "Tapu_Koko",
    'tapu-lele': "Tapu_Lele",
    'tapu-bulu': "Tapu_Bulu",
    'tapu-fini': "Tapu_Fini",
    'great-tusk': "Great_Tusk",
    'scream-tail': "Scream_Tail",
    'brute-bonnet': "Brute_Bonnet",
    'flutter-mane': "Flutter_Mane",
    'slither-wing': "Slither_Wing",
    'sandy-shocks': "Sandy_Shocks",
    'iron-treads': "Iron_Treads",
    'iron-bundle': "Iron_Bundle",
    'iron-hands': "Iron_Hands",
    'iron-jugulis': "Iron_Jugulis",
    'iron-moth': "Iron_Moth",
    'iron-thorns': "Iron_Thorns",
    'roaring-moon': "Roaring_Moon",
    'iron-valiant': "Iron_Valiant",
    'walking-wake': "Walking_Wake",
    'iron-leaves': "Iron_Leaves",
    'gouging-fire': "Gouging_Fire",
    'raging-bolt': "Raging_Bolt",
    'iron-boulder': "Iron_Boulder",
    'iron-crown': "Iron_Crown",
    'magearna-original': "Magearna",
    'minior-red-meteor': "Minior",
    'darmanitan-standard': "Darmanitan",
    'indeedee-male': "Indeedee",
    'morpeko-full-belly': "Morpeko",
    'pumpkaboo-average': "Pumpkaboo",
    'gourgeist-average': "Gourgeist",
    'aegislash-shield': "Aegislash",
    'deoxys-normal': "Deoxys",
    'wormadam-plant': "Wormadam",
    'giratina-altered': "Giratina",
    'shaymin-land': "Shaymin",
    'basculin-red-striped': "Basculin",
    'tornadus-incarnate': "Tornadus",
    'thundurus-incarnate': "Thundurus",
    'landorus-incarnate': "Landorus",
    'keldeo-ordinary': "Keldeo",
    'meloetta-aria': "Meloetta",
    'meowstic-male': "Meowstic",
    'zygarde-50': "Zygarde",
    'oricorio-baile': "Oricorio",
    'lycanroc-midday': "Lycanroc",
    'wishiwashi-solo': "Wishiwashi",
    'mimikyu-disguised': "Mimikyu",
    'toxtricity-amped': "Toxtricity",
    'eiscue-ice': "Eiscue",
    'urshifu-single-strike': "Urshifu",
    'basculegion-male': "Basculegion",
    'enamorus-incarnate': "Enamorus",
    'flabebe': "Flabébé",
}

# Sanitize Pokémon name for safe folder creation
def sanitize_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Function to create directories for each Pokémon
def create_folder(pokemon_name):
    sanitized_name = sanitize_name(pokemon_name)
    folder = f"Training{sanitized_name}"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

# Function to load excluded Pokémon from a text file
def load_excluded_pokemon(file_path):
    excluded_pokemon = set()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                excluded_pokemon.add(line.strip().lower())
    return excluded_pokemon

# Asynchronous function to download an image from a given URL with retries
async def download_image(session, image_url, save_path, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(image_url, timeout=30) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with open(save_path, "wb") as img_file:
                        img_file.write(img_data)
                    print(f"Downloaded {save_path}")
                    return
                else:
                    print(f"Failed to download {image_url}, status code: {response.status}")
        except Exception as e:
            if attempt < retries - 1:
                print(f"Retrying {image_url} ({attempt + 1}/{retries})...")
                await asyncio.sleep(2)  # Backoff before retrying
            else:
                print(f"Failed to download {image_url} after {retries} attempts: {e}")

# Function to extract Dex number from Pokémon's name in the URL
def extract_dex_number(pokemon_name, image_name):
    # Match the Pokémon name's Dex number at the start of the filename (like 0811Thwackey)
    dex_number = re.search(r"(\d{3,4})", image_name)
    if dex_number:
        dex_number_str = dex_number.group(1)
        # Ensure that the dex number matches the Pokémon's index
        return dex_number_str in image_name
    return False

# Asynchronous function to scrape and download high-quality images for a single Pokémon
async def scrape_pokemon_images(session, pokemon, idx, semaphore):
    async with semaphore:
        pokemon_name = NAME_MAPPING.get(pokemon, pokemon.capitalize())
        print(f"Scraping high-quality images for {pokemon_name}...")

        # Search page for Pokémon images on Bulbapedia
        search_url = f"https://archives.bulbagarden.net/wiki/Category:{pokemon_name}"
        try:
            async with session.get(search_url, timeout=30) as response:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, "html.parser")
        except asyncio.TimeoutError:
            print(f"Timeout while accessing {search_url}")
            return

        # Find all anchor tags that link to image pages
        image_links = soup.select("a.image")
        image_urls = []

        for a_tag in image_links:
            # Get the full-size image link from the image page
            img_page_url = "https://archives.bulbagarden.net" + a_tag["href"]
            try:
                async with session.get(img_page_url, timeout=30) as img_page_response:
                    img_page_content = await img_page_response.text()
                    img_soup = BeautifulSoup(img_page_content, "html.parser")
                    full_img_tag = img_soup.select_one(".fullImageLink a")
                    if full_img_tag:
                        full_img_url = full_img_tag["href"]
                        if not full_img_url.startswith("https:"):
                            full_img_url = "https:" + full_img_url
                        # Extract file name from URL
                        image_name = os.path.basename(full_img_url)
                        if extract_dex_number(pokemon_name, image_name):
                            image_urls.append(full_img_url)
            except Exception as e:
                print(f"Failed to retrieve image page {img_page_url}: {e}")

        # Download high-quality images
        folder = create_folder(pokemon_name)
        tasks = []
        for i, img_url in enumerate(image_urls[:20]):  # Limit to 50 images per Pokémon
            save_path = f"{folder}/{pokemon_name}_{i + 1}.png"
            tasks.append(download_image(session, img_url, save_path))

        # Run all download tasks concurrently
        await asyncio.gather(*tasks)

        # If fewer than 50 images were downloaded, use Bing Images to fill in the rest
        images_needed = 20 - len(image_urls)
        if images_needed > 0:
            print(f"Only {len(image_urls)} images found on Bulbapedia for {pokemon_name}. Searching on Bing Images for {images_needed} more images...")
            search_query = f"{pokemon_name} pokemon official artwork bulbapedia pokemondb serebii fanart png high quality"
            downloader.download(search_query, limit=images_needed, output_dir='Training', adult_filter_off=True, force_replace=False, timeout=60)

        print(f"Finished scraping images for {pokemon_name}")

# Asynchronous function to scrape and download images for all Pokémon
async def scrape_all_pokemon(pokemon_names, excluded_pokemon):
    semaphore = asyncio.Semaphore(10)  # Increase the number of concurrent requests
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        tasks = []
        for idx, pokemon in enumerate(pokemon_names):
            if pokemon.lower() not in excluded_pokemon:  # Skip excluded Pokémon
                tasks.append(scrape_pokemon_images(session, pokemon, idx, semaphore))
            else:
                print(f"Skipping {pokemon} as it's in the exclusion list.")
        await asyncio.gather(*tasks)

# Main entry point
async def main():
    # Retrieve All Pokémon Names asynchronously
    url = "https://pokeapi.co/api/v2/pokemon/?limit=10000"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    # Storing Pokémon names
    pokemonNames = [i["name"] for i in data["results"]]
    
    # Load excluded Pokémon from a text file
    excluded_pokemon = load_excluded_pokemon("filtered_pokemon_names.txt")

    await scrape_all_pokemon(pokemonNames, excluded_pokemon)

    print("Image scraping completed.")

if __name__ == "__main__":
    if os.name == 'nt':
        # Switch event loop policy on Windows to avoid issues
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
