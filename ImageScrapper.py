import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os

# Function to create directories for each Pokémon
def create_folder(pokemon_name):
    folder = f"downloads/{pokemon_name}"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

# Asynchronous function to download an image from a given URL with retries
async def download_image(session, image_url, save_path, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(image_url, timeout=10) as response:
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

# Handle Pokémon with exceptional names
exceptionalPokemonNames = {
    29: "Nidoran",
    32: "Nidoran",
    83: "Farfetch%27d",
    122: "Mr._Mime",
    250: "Ho-Oh",
    386: "Deoxys",
    413: "Wormadam-Plant",
    474: "Porygon-Z",
    487: "Giratina",
    492: "Shaymin",
    550: "Basculin-Red",
    555: "Darmanitan",
    641: "Tornadus",
    642: "Thundurus",
    645: "Landorus",
    647: "Keldeo",
    648: "Meloetta",
    669: "Flabébé",
    678: "Meowstic",
    681: "Aegislash-Shield",
    710: "Pumpkaboo",
    711: "Gourgeist",
    718: "Zygarde",
    741: "Oricorio",
    745: "Lycanroc",
    746: "Wishiwashi",
    774: "Minior",
    778: "Mimikyu",
    782: "Jangmo-o",
    783: "Hakamo-o",
    784: "Kommo-o",
    849: "Toxtricity-Amped",
    865: "Sirfetch'd",
    866: "Mr. Rime",
    875: "Eiscue",
    876: "Indeedee",
    877: "Morpeko-Full",
    892: "Urshifu-Single_Strike",
    902: "Basculegion",
    905: "Enamorus",
    1001: "Wo-Chien",
    1002: "Chien-Pao",
    1003: "Ting-Lu",
    1004: "Chi-Yu",
}

# Asynchronous function to scrape and download images for a single Pokémon
async def scrape_pokemon_images(session, pokemon, idx, semaphore):
    async with semaphore:
        pokemon_name = exceptionalPokemonNames.get(idx, pokemon.capitalize())

        print(f"Scraping images for {pokemon_name}...")

        # Search page for Pokémon images on Bulbapedia
        search_url = f"https://archives.bulbagarden.net/wiki/Category:{pokemon_name}"
        try:
            async with session.get(search_url, timeout=10) as response:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, "html.parser")
        except Exception as e:
            print(f"Failed to retrieve page for {pokemon_name}: {e}")
            return

        # Find all anchor tags that link to image pages
        image_links = soup.select("a.image")
        image_urls = []
        for a_tag in image_links:
            # Get the URL for the image page
            img_page_url = "https://archives.bulbagarden.net" + a_tag["href"]

            # Go to the image page and extract the full-size image link
            try:
                async with session.get(img_page_url, timeout=10) as img_page_response:
                    img_page_content = await img_page_response.text()
                    img_soup = BeautifulSoup(img_page_content, "html.parser")
                    full_img_tag = img_soup.select_one(".fullImageLink a")

                    if full_img_tag:
                        full_img_url = full_img_tag["href"]
                        if not full_img_url.startswith("https:"):
                            full_img_url = "https:" + full_img_url
                        image_urls.append(full_img_url)
            except Exception as e:
                print(f"Failed to retrieve image page {img_page_url}: {e}")

        # Download up to 25 images
        folder = create_folder(pokemon_name)
        tasks = []
        for i, img_url in enumerate(image_urls[:25]):  # Limit to 25 images per Pokémon
            save_path = f"{folder}/{pokemon_name}_{i + 1}.png"
            tasks.append(download_image(session, img_url, save_path))

        # Run all download tasks concurrently
        await asyncio.gather(*tasks)

        print(f"Finished scraping images for {pokemon_name}")

# Asynchronous function to scrape and download images for all Pokémon
async def scrape_all_pokemon(pokemon_names):
    semaphore = asyncio.Semaphore(5)  # Limit concurrent requests to 5
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, pokemon in enumerate(pokemon_names):
            tasks.append(scrape_pokemon_images(session, pokemon, idx, semaphore))
        await asyncio.gather(*tasks)

# Main entry point
async def main():
    # Retrieve All Pokémon Names asynchronously
    url = "https://pokeapi.co/api/v2/pokemon/?limit=1025"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    # Storing Pokémon names
    pokemonNames = [i["name"] for i in data["results"]]

    await scrape_all_pokemon(pokemonNames)

    print("Image scraping completed.")

if __name__ == "__main__":
    if os.name == 'nt':
        # Switch to SelectorEventLoopPolicy to avoid ProactorEventLoop issues
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
