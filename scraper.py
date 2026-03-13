import logging
from collected_data import OzonCollectedData
from searcher import OzonSearcher

class OzonScraper:
    def __init__(self):
        self.logger = logging.getLogger("OzonScraper")
        self.searcher = OzonSearcher()
        self.data = OzonCollectedData()

    async def gather_info(self, item_name: str):
        self.logger.info(f"Gather Info: {item_name}")
        self.logger.info("Calling a searcher...")
        await self.searcher.search_info(item_name)

        