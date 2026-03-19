from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from collected_data import OzonCollectedData
from ozon_item import OzonItem
from selectolax.lexbor import LexborHTMLParser, LexborNode
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
    
    async def start(self, use_headless = True):
        self.logger.info("Start - Beginning.")

        self.logger.info("Starting Playwright...")
        self.playwright_manager = Stealth().use_async(async_playwright())
        self.playwright = await self.playwright_manager.__aenter__()
        self.logger.info("Playwright started!")

        self.logger.info("Launching a browser...")
        self.browser = await self.playwright.chromium.launch(
            #headless = True,
            headless = use_headless,
            channel = "chromium", # For WebGL to work in headless mode
            args = [
                # I don't know what are these arguments, I just have stolen them
                # from here:
                # https://github.com/Xammatov/Ozon_Parser/blob/main/parser.py
                # Their descriptions make them look very *helpful*
                # I mean it kinda works even without those arguments, but I'd rather keep them
                "--disable-blink-features=AutomationControlled",
                "--disable-features=UserAgentClientHint",
                #"--headless=new",
                #"--use-gl=osmesa",
                #
                # And that bunch of arguments is needed to make WebGL work in
                # headless mode. One of the reasons why headless mode failed
                # when entering the Ozon website is because WebGL tests had failed.
                # UPDATE: Actually, they aren't required for WebGL to function normally...
                # Whatever, I'll just keep them here.
                #
                "--use-angle=vulkan",
                "--enable-features=Vulkan",
                "--disable-vulkan-surface",
                "--enable-unsafe-webgpu",  # Also enables WebGPU if needed
                "--ignore-gpu-blocklist",
                # "--enable-gpu",
                # "--enable-webgl",
                "--use-gl=desktop",  # Force desktop GL over SwiftShader
                "--no-sandbox",  # Often needed in containerized environments
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

            content = await self.page.content()
            parser = LexborHTMLParser(content)

            grids = parser.css('div[data-widget="tileGridDesktop"]')
            for grid in grids:
                for child in grid.iter():
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
    
    async def parse_grid_element(self, child: LexborNode, item: OzonItem) -> bool:
        tags = list(child.iter())
        new_tags = []

        #self.logger.info("parse_grid_element - Tags~")
        for tag in tags:
            if tag.tag == "-comment":
                continue
            #self.logger.info(f"Tag {tag.tag} {tag.tag_id}")
            new_tags.append(tag)
        tags = new_tags
            
        a_link = tags[0]
        if a_link:
            url = a_link.attributes.get("href")
            if not url or self.parsed_URLs.get(url, False):
                return False
            
            item.url = url
            self.parsed_URLs[url] = True
        else:
            self.logger.error("Couldn't access <a> tag at parse_grid_element")
            return False

        bottom_div = tags[1]
        if bottom_div:
            await self.parse_grid_bottom_element(bottom_div, item)
        else:
            self.logger.error("Couldn't access a 'bottom' <div> at parse_grid_element")

        return True
    
    async def parse_grid_bottom_element(self, bottom_div: LexborNode, item: OzonItem):
        a_name = bottom_div.css_first("a")
        if a_name:
            item.name = a_name.text(strip=True)
        else:
            self.logger.error("Couldn't access <a> tag at parse_grid_bottom_element")

        children = list(bottom_div.iter())
        
        if children:
            div_price = children[0]
            item.price = await self.parse_price_div(div_price)
        else:
            self.logger.error("No children available at parse_grid_bottom_element")

        for child in children:
            elements = list(child.iter())
            if len(elements) != 2:
                continue
            if elements[0].tag == "span" and elements[1].tag == "span":
                if len(list(elements[0].iter())) == 2:
                    div_rating = child
                    rating, ratings_amount = await self.parse_rating_div(div_rating)
                    item.rating = rating
                    item.ratings_amount = ratings_amount
                    break
    
    def extract_numbers_regex(self, text):
        """Extract only digits using regex"""
        return re.sub(r'\D', '', text)  # \D matches any non-digit character
    
    def get_first_child_of_node(self, node: LexborNode) -> LexborNode:
        return node.iter().__next__() if node.iter() else None

    async def parse_price_div(self, div_price: LexborNode) -> str:
        first_child = self.get_first_child_of_node(div_price)
        if first_child:
            span_price = self.get_first_child_of_node(first_child)
            if span_price:
                price_text = span_price.text(deep=False)
                price_text = price_text.split(" ")[0]  # This tiny space is a fucking nightmare fuel
                price_text = price_text.replace(",", ".")
                return price_text
            else:
                self.logger.error("Couldn't access a span_price at parse_price_div")
        else:
            self.logger.error("Couldn't access a first_child at parse_price_div")
        return ""
    
    async def parse_rating_div(self, div_rating: LexborNode) -> tuple[str, str]:
        children = list(div_rating.iter())
        rating = children[0].text() if children else ""
        ratings_amount = children[1].text() if len(children) > 1 else ""
        ratings_amount = self.extract_numbers_regex(ratings_amount)
        return rating, ratings_amount