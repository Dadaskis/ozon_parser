import asyncio
import config
import logging
import re
import platform
from scraper import OzonScraper

async def get_input(prompt: str) -> str:
    """Async version of input() that works with asyncio"""
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
    except asyncio.exceptions.CancelledError:
        raise KeyboardInterrupt()

def extract_max_value(text):
    """Extract number after 'max:' pattern"""
    match = re.search(r'max:(\d+)', text)
    return int(match.group(1)) if match else None

def clean_string_regex(text):
    """Remove //max: with any value and //desc, then strip"""
    # Remove //max: followed by any digits
    text = re.sub(r'//max:\d+\s*', '', text)
    # Remove //desc
    text = re.sub(r'//desc\s*', '', text)
    # Strip whitespace
    return text.strip()

async def main():
    logger = logging.getLogger("Main")
    logger.info("Ozon Scraper start!")
    scraper = OzonScraper()

    use_headless = True
    if platform.system() == "Linux":
        logger.warning("Disabling headless mode for Linux compatibility")
        use_headless = False

    await scraper.start(use_headless=use_headless)

    try:
        while True:
            print("\n" * 3)
            print("=" * 50)
            
            print("Ozon Parser")
            print("[Argument] //desc     -   Parse descriptions (off by default [BE CAUTIOUS, SLOW OPTION])")
            print("[Argument] //max:100  -   Set maximum limit of items processed in searcher (100 by default)")
            print("[Argument] //exit     -   Complete this program")
            print("Example input: Headphones //max:200 //desc")
            print()

            item_name = await get_input("Enter item name to search: ")
            print("=" * 50)
            print("\n" * 3)

            if item_name == "//exit":
                raise KeyboardInterrupt()

            max_items = 100
            if "//max" in item_name:
                max_items = extract_max_value(item_name)
            
            collect_desc = "//desc" in item_name

            item_name = clean_string_regex(item_name)

            await scraper.gather_info(item_name, max_items, collect_desc)
    except KeyboardInterrupt:
        print("\n")
        print("=" * 50)
        print("\n" * 3)
        logger.info("Stopping the program!")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())