from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from collected_data import OzonCollectedData
import logging
import asyncio

class OzonSearcher:
    def __init__(self):
        self.logger = logging.getLogger("OzonSearcher")
        self.browser = None
        self.playwright_manager = None
        self.playwright = None
        self.page = None
    
    async def start(self):
        self.logger.info("Start - Beginning.")

        self.logger.info("Starting Playwright...")
        self.playwright_manager = Stealth().use_async(async_playwright())
        self.playwright = await self.playwright_manager.__aenter__()
        self.logger.info("Playwright started!")

        self.logger.info("Launching a browser...")
        self.browser = await self.playwright.chromium.launch(
            headless = True,
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
        except:
            pass
        self.logger.info("Stop - Ending.")

    async def search_info(self, item_name: str):
        self.logger.info(f"Searching Info: {item_name}")

        self.logger.info(f"Using a searchbar to search '{item_name}'...")
        search_box = self.page.locator("input")
        await search_box.fill(item_name)
        await search_box.press("Enter")

        self.logger.info("Waiting for the page to load...")
        await self.page.wait_for_load_state("networkidle")

        return await self.parse_the_grid()

        # self.logger.info("Exporting HTML to DEBUG_OUTPUT.html")
        # content = await self.page.content()
        # with open("DEBUG_OUTPUT.html", "w", encoding="utf-8") as file:
        #     file.write(content)\
    
    async def parse_the_grid(self) -> OzonCollectedData:
        pass
            
