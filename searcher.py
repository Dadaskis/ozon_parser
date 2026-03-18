from playwright.async_api import async_playwright, Locator
from playwright_stealth import Stealth
from collected_data import OzonCollectedData
from ozon_item import OzonItem
from bs4 import BeautifulSoup, PageElement
import logging
import asyncio
import re

class OzonSearcher:
    def __init__(self):
        self.logger = logging.getLogger("OzonSearcher")
        self.browser = None
        self.playwright_manager = None
        self.playwright = None
        self.page = None
        self.previous_search_value = ""
        self.parsed_URLs = {}
    
    async def start(self):
        self.logger.info("Start - Beginning.")

        self.logger.info("Starting Playwright...")
        self.playwright_manager = Stealth().use_async(async_playwright())
        self.playwright = await self.playwright_manager.__aenter__()
        self.logger.info("Playwright started!")

        self.logger.info("Launching a browser...")
        self.browser = await self.playwright.chromium.launch(
            headless = True,
            #headless = False,
            channel = "chromium", # For WebGL to work in headless mode
            args = [
                # I don't know what are these arguments, I just have stolen them
                # from here:
                # https://github.com/Xammatov/Ozon_Parser/blob/main/parser.py
                # Their descriptions make them look very *helpful*
                # I mean it kinda works even without those arguments, but I'd rather keep them
                "--disable-blink-features=AutomationControlled",
                "--disable-features=UserAgentClientHint",
                #
                # And that bunch of arguments is needed to make WebGL work in
                # headless mode. One of the reasons why headless mode failed
                # when entering the Ozon website is because WebGL tests had failed.
                # UPDATE: Actually, they aren't required for WebGL to function normally...
                # Whatever, I'll just keep them here.
                #
                # "--use-angle=vulkan",
                # "--enable-features=Vulkan",
                # "--disable-vulkan-surface",
                # "--enable-unsafe-webgpu",  # Also enables WebGPU if needed
                # "--ignore-gpu-blocklist",
                # "--enable-gpu",
                # "--enable-webgl",
                # "--use-gl=desktop",  # Force desktop GL over SwiftShader
                # "--no-sandbox",  # Often needed in containerized environments
            ]
        )
        self.logger.info("Browser is intact!")

        self.logger.info("Creating a page...")
        self.page = await self.browser.new_page()
        
        self.logger.info("Going to ozon.by...")
        await self.page.goto("https://ozon.by")
        
        self.logger.info("Waiting for the page to pass the bot test - 3 seconds...")
        await asyncio.sleep(3.0)
        
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

    async def search_info(self, item_name: str, max_items: int, desc_queue: asyncio.Queue, col_data: OzonCollectedData):
        self.logger.info(f"Searching Info: {item_name}")

        self.logger.info(f"Using a searchbar to search '{item_name}'...")
        search_box = None
        if self.previous_search_value != "":
            search_box = self.page.locator(f'input[value="{self.previous_search_value}"]')
        else:
            search_box = self.page.locator("input")
        await search_box.fill(item_name)
        await search_box.press("Enter")
        self.parsed_URLs.clear()

        self.logger.info("Waiting for the page to load...")
        await self.page.wait_for_load_state("networkidle")

        # self.logger.info("Exporting HTML to DEBUG_OUTPUT.html")
        # content = await self.page.content()
        # with open("DEBUG_OUTPUT.html", "w", encoding="utf-8") as file:
        #     file.write(content)
        
        self.previous_search_value = item_name

        await self.parse_the_grid(max_items, desc_queue, col_data)
    
    async def parse_the_grid(self, max_items: int, desc_queue: asyncio.Queue, data: OzonCollectedData):
        item_difference = 1

        counter = 0

        while item_difference > 0:
            items_count_before = data.get_count()

            #content = await self.page.content()
            #bs = BeautifulSoup(content, features="lxml")

            #grids = bs.find_all("div", attrs = {"data-widget" : "tileGridDesktop"})

            grids = await self.page.locator('div[data-widget="tileGridDesktop"]').all()

            for grid in grids:
                for child in await grid.locator("> *").all():
                    item = OzonItem()
                    can_be_added = await self.parse_grid_element(child, item)
                    if can_be_added:
                        data.add_item(item)
                        await desc_queue.put(item)
                        counter += 1
                        self.logger.info(f"Items processed: {counter}")
            
            items_count_after = data.get_count()

            item_difference = items_count_after - items_count_before

            if data.get_count() > max_items:
                self.logger.info("Hitting a limit!")
                break
            
            for _ in range(5):
                await self.page.mouse.wheel(0, 500)
                await asyncio.sleep(0.5)
        
        #data.debug_print()

        self.logger.info("Queue shutdown!")

        desc_queue.shutdown()
    
    async def parse_grid_element(self, child: Locator, item: OzonItem) -> bool:
        #tags = child.find_all(recursive=False)
        tags = await child.locator("> *").all()
            
        a_link = tags[0]
        
        url = await a_link.get_attribute("href")
        if self.parsed_URLs.get(url, False) == True:
            return False
        
        item.url = url
        self.parsed_URLs[url] = True

        bottom_div = tags[1]
        await self.parse_grid_bottom_element(bottom_div, item)

        return True
    
    async def parse_grid_bottom_element(self, bottom_div: Locator, item: OzonItem):
        children = await bottom_div.locator("> *").all()

        a_name = (await bottom_div.locator("a").all())[0]
        item.name = await a_name.text_content()

        div_price = children[0]
        item.price = await self.parse_price_div(div_price)

        div_rating = None
        for child in children:
            elements = await child.locator("> *").all()
            if len(elements) != 2:
                continue
            elem0_name = await elements[0].evaluate("el => el.tagName")
            elem1_name = await elements[1].evaluate("el => el.tagName")
            if elem0_name == "span" and elem1_name == "span":
                if len(await elements[0].locator("> *").all()) == 2:
                    div_rating = child
        if div_rating:
            rating, ratings_amount = await self.parse_rating_div(div_rating)
            item.rating = rating
            item.ratings_amount = ratings_amount
    
    def extract_numbers_regex(self, text):
        """Extract only digits using regex"""
        return re.sub(r'\D', '', text)  # \D matches any non-digit character
    
    async def parse_price_div(self, div_price: Locator) -> str:
        div_price = (await div_price.locator("> *").all())[0]
        span_price = (await div_price.locator("> *").all())[0]
        price_text = await span_price.text_content()
        price_text = price_text.split(" ")[0] # This tiny space is a fucking nightmare fuel
        price_text = price_text.replace(",", ".")
        return price_text
    
    async def parse_rating_div(self, div_rating: Locator) -> tuple[str, str]:
        children = await div_rating.locator("> *").all()
        rating = await children[0].text_content()
        ratings_amount = await children[1].text_content()
        ratings_amount = self.extract_numbers_regex(ratings_amount)
        return rating, ratings_amount