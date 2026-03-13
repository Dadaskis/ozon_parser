import logging
import time
import asyncio
from collected_data import OzonCollectedData
from searcher import OzonSearcher
from desc_peeker import OzonDescriptionPeeker

class OzonScraper:
    def __init__(self):
        self.logger = logging.getLogger("OzonScraper")
        self.searcher = OzonSearcher()
        self.desc_peeker = OzonDescriptionPeeker()
        self.data = OzonCollectedData()

    async def start(self):
        self.logger.info("Start - Beginning.")
        tasks = [
            self.searcher.start(),
            self.desc_peeker.start()
        ]
        await asyncio.gather(*tasks)
        self.logger.info("Start - Finished.")
    
    async def stop(self):
        self.logger.info("Stop - Beginning.")
        await self.searcher.stop()
        await self.desc_peeker.stop()
        self.logger.info("Stop - Ending.")

    async def gather_info(self, item_name: str, max_items: int, collect_desc: bool):
        start_time = time.time()

        self.logger.info(f"Gather Info: {item_name}")
        
        self.logger.info("Calling a searcher...")
        data = await self.searcher.search_info(item_name, max_items)

        if collect_desc:
            await self.desc_peeker.fill_descriptions(data)

        data.save_file(item_name)

        end_time = time.time()
        execution_time = end_time - start_time

        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = execution_time % 60
        self.logger.info(f"Info gathered in {hours}h {minutes}m {seconds:.2f}s")

        