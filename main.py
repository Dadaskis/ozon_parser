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
            headless = True,
            channel = "chromium", # For WebGL to work in headless mode
            args = [
                # I don't know what are these arguments, I just have stolen them
                # from here:
                # https://github.com/Xammatov/Ozon_Parser/blob/main/parser.py
                # Their descriptions make them look very *helpful*
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
        
        page = await browser.new_page()
        await page.goto("https://ozon.by/")
        
        await asyncio.sleep(4.0)
        
        #await page.goto("https://intoli.com/blog/making-chrome-headless-undetectable/chrome-headless-test.html")
        #await page.goto("https://www.whatismybrowser.com/")
        #await page.goto("chrome://version")
        
        content = await page.content()
        with open("output1.html", "w", encoding="utf-8") as file:
            file.write(content)
        
        #print("Press Enter to die :)")
        #input()

        # webgl_status = await page.evaluate("""
        #     () => {
        #         const canvas = document.createElement('canvas');
        #         const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
        #         if (!gl) return 'WebGL not available';
        #         const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        #         if (debugInfo) {
        #             return {
        #                 vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
        #                 renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
        #             };
        #         }
        #         return 'WebGL available but renderer info masked';
        #     }
        # """)
        # print("WebGL Status:", webgl_status)
        
        await browser.close()

    print("Main - End")

if __name__ == "__main__":
    asyncio.run(main())