from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import logging
import asyncio

class OzonSearcher:
    def __init__(self):
        self.logger = logging.getLogger("OzonScraper")

    async def gather_info(self, item_name: str):
        self.logger.info(f"Gather Info: {item_name}")
        self.logger.info("Starting Playwright...")
        async with Stealth().use_async(async_playwright()) as playwright:
            self.logger.info("Playwright online!")
            self.logger.info("Launching a browser...")
            browser = await playwright.chromium.launch(
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
                    # when entering Ozon website is because WebGL tests had failed.
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
            page = await browser.new_page()
            self.logger.info("Going to ozon.by...")
            await page.goto("https://ozon.by")
            self.logger.info("Waiting for the page to load - 5 seconds...")
            await asyncio.sleep(5.0)
            self.logger.info("Waiting is over, obtaining the page content.")
            content = await page.content()
            self.logger.info(f"HTML length: {len(content)}")
            
