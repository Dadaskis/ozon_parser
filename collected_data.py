import pandas as pd
import os
from ozon_item import OzonItem

class OzonCollectedData:
    def __init__(self):
        self.df = pd.DataFrame()
    
    def add_item(self, item: OzonItem) -> int:
        item_dict = item.get_pandas_dict()
        new_df = pd.DataFrame(item_dict)
        index = len(self.df)
        item.index = index
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        return index
    
    def save_file(self, file_name: str):
        if not os.path.exists("export/"):
            os.mkdir("export/")
        self.df.to_csv(f"export/{file_name}")