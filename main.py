from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import asyncio
import random

async def main():
    print("Main - Start")
    
    stealth = Stealth()
    #stealth.

    async with stealth.use_async(async_playwright()) as playwright:
    #async with async_playwright() as playwright:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ]

        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                #'--no-sandbox',
                #'--disable-dev-shm-usage',
                #'--disable-gpu',
                #'--disable-extensions',
                #'--disable-setuid-sandbox',
                #'--disable-blink-features=AutomationControlled',
                #'--disable-features=UserAgentClientHint',
                #'--window-size=1920,1080',
                #'--start-maximized',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(user_agents),
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        )

        await stealth.apply_stealth_async(context)
        
        await context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en']
            });
            
            // Override chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # Create a new page
        page = await context.new_page()

        #page = await browser.new_page()
        await page.goto("https://ozon.by/")
        await asyncio.sleep(20.0)
        #await page.goto("https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html")
        #await page.goto("https://www.whatismybrowser.com/")
        #await page.goto("chrome://version")
        content = await page.content()
        with open("output1.html", "w", encoding="utf-8") as file:
            file.write(content)
        #print("Press Enter to die :)")
        #input()
        await browser.close()

    print("Main - End")

if __name__ == "__main__":
    asyncio.run(main())