from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from collected_data import OzonCollectedData
from ozon_item import OzonItem
from bs4 import BeautifulSoup, PageElement
import logging
import asyncio
import re

class OzonDescriptionPeeker:
    def __init__(self):
        self.logger = logging.getLogger("OzonDescriptionPeeker")
        self.browser = None
        self.playwright_manager = None
        self.playwright = None
        self.page = None
        self.previous_search_value = ""
        self.parsed_URLs = {}
    
    async def start(self, use_headless = True):
        self.logger.info("Start - Beginning.")

        self.logger.info("Starting Playwright...")
        self.playwright_manager = Stealth().use_async(async_playwright())
        self.playwright = await self.playwright_manager.__aenter__()
        self.logger.info("Playwright started!")

        self.logger.info("Launching a browser...")
        self.browser = await self.playwright.chromium.launch(
            headless = use_headless,
            #headless = False,
            channel = "chromium", # For WebGL to work in headless mode
            args = [
                # A bunch of comments were removed from here, take a look at searcher.py
                "--disable-blink-features=AutomationControlled",
                "--disable-features=UserAgentClientHint"
            ]
        )
        self.logger.info("Browser is intact!")

        self.logger.info("Creating a page...")
        self.page = await self.browser.new_page()

        self.logger.info("Going to ozon.by...")
        await self.page.goto("https://ozon.by")
        
        self.logger.info("Waiting for the page to pass the bot test - 3 seconds...")
        await asyncio.sleep(3.0)

        #html = await self.page.content()
        #if "document.querySelector('.challenge-information');" in html:
        #    raise Exception("We didn't pass the bot check")
        
        self.logger.info("Waiting for the page to load fully...")
        await self.page.wait_for_load_state("networkidle")

        self.logger.info("Start - Ending.")
    
    async def stop(self):
        self.logger.info("Stop - Beginning.")
        try:
            await self.browser.close()
            await self.playwright_manager.__aexit__(None, None, None)
        except Exception:
            self.logger.error("Exception occured during shutdown", exc_info=True)
        self.logger.info("Stop - Ending.")
    
    async def fill_descriptions(self, queue: asyncio.Queue, col_data: OzonCollectedData):
        counter = 0
        try:
            while True:
                data = await queue.get()

                url = f"https://ozon.by{data.url}"

                self.logger.info(f"Processing description [{counter}/{queue.qsize()}]")

                if data.description != "Undefined":
                    counter += 1
                    continue

                #self.logger.info(url)
                
                await self.page.goto(url)
                await asyncio.sleep(3.0)
                await self.page.wait_for_load_state("networkidle")

                # self.logger.info("Exporting HTML to DEBUG_OUTPUT.html")
                # content = await self.page.content()
                # with open("DEBUG_OUTPUT.html", "w", encoding="utf-8") as file:
                #     file.write(content)

                try: 
                    content = await self.page.content()
                    bs = BeautifulSoup(content, features="lxml")
                    desc = bs.find("div", id="section-description").get_text()
                    data.description = desc
                except Exception:
                    self.logger.error("Failed to fetch a description", exc_info=True)
                    data.description = "Error"
                
                col_data.add_item(data)

                counter += 1
        except asyncio.QueueShutDown:
            self.logger.info("Descriptions done!")