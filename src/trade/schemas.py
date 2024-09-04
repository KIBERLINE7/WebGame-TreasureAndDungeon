from pydantic import BaseModel

class Buy_items (BaseModel):
    items_id: int

class Sell_items (BaseModel):
    items_id: int