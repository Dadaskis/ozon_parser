import asyncio
import config
from scraper import OzonScraper

async def main():
    print("Ozon Scraper start!")
    scraper = OzonScraper()
    await scraper.gather_info("Test!")

if __name__ == "__main__":
    asyncio.run(main())