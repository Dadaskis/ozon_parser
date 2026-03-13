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

item1_upd = OzonItem()
item1_upd.name = "Newest thingy"
item1_upd.rating = "5.0"
item1_upd.ratings_amount = "1338"
item1_upd.price = "100 BYN"
item1_upd.description = "Lorem ipsum dolor sit amen."

print(data.add_item(item0))
print(data.add_item(item1))

item1_upd.index = item1.index

print(item0.index)
print(item1.index)

data.add_item(item1_upd)

data.debug_print()
data.save_file("special")
