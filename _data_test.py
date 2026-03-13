from ozon_item import OzonItem
from collected_data import OzonCollectedData

data = OzonCollectedData()

item0 = OzonItem()

item1 = OzonItem()
item1.name = "New thingy"
item1.rating = "5.0"
item1.ratings_amount = "1337"
item1.price = "100 BYN"
item1.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean non nibh erat. Vivamus in luctus nibh. Fusce commodo lacus commodo, laoreet arcu at, lacinia enim. "

print(data.add_item(item0))
print(data.add_item(item1))

print(item0.index)
print(item1.index)

print(data.df.to_string(max_colwidth=40))
data.save_file("special")
