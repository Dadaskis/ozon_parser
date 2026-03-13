from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import asyncio

async def main():
    print("Main - Start")
    
    stealth = Stealth()
    #stealth.

    async with stealth.use_async(async_playwright()) as playwright:
    #async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=UserAgentClientHint"
            ]
        )
        page = await browser.new_page()
        await page.goto("https://ozon.by/")
        #await page.goto("https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html")
        #await asyncio.sleep(20.0)
        #await page.goto("https://www.whatismybrowser.com/")
        #await page.goto("chrome://version")
        #content = await page.content()
        #with open("output1.html", "w", encoding="utf-8") as file:
            #file.write(content)
        print("Press Enter to die :)")
        input()
        await browser.close()

    print("Main - End")

if __name__ == "__main__":
    asyncio.run(main())