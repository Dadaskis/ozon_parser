class OzonItem:
    name: str
    rating: str
    ratings_amount: str
    price: str
    description: str
    url: str
    index: int

    def __init__(self):
        self.name = "Undefined"
        self.rating = "0.0"
        self.ratings_amount = "0"
        self.price = "0"
        self.description = "Undefined"
        self.index = 0
        self.url = "https://ozon.by/404"

    def get_pandas_dict(self):
        return {
            "name": [self.name],
            "rating": [self.rating],
            "ratings_amount": [self.ratings_amount],
            "price": [self.price],
            "description": [self.description],
            "url": [self.url]
        }