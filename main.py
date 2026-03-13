import asyncio
import config
import logging
from scraper import OzonScraper

async def get_input(prompt: str) -> str:
    """Async version of input() that works with asyncio"""
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
    except asyncio.exceptions.CancelledError:
        raise KeyboardInterrupt()

async def main():
    logger = logging.getLogger("Main")
    logger.info("Ozon Scraper start!")
    scraper = OzonScraper()
    await scraper.start()

    try:
        while True:
            print("\n" * 3)
            print("=" * 50)
            print("Ozon Parser")
            print("[Argument] //desc - Parse descriptions (off by default)")
            print("[Argument] //exit - Complete this program")
            item_name = await get_input("Enter item name to search: ")
            print("=" * 50)
            print("\n" * 3)
            if item_name == "//exit":
                raise KeyboardInterrupt()
            await scraper.gather_info(item_name)
    except KeyboardInterrupt:
        print("\n")
        print("=" * 50)
        print("\n" * 3)
        logger.info("Stopping the program!")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())