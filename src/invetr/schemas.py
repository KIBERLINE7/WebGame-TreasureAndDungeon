from pydantic import BaseModel

class Enter_Nick (BaseModel):
    nickname : str
class Enter_Swap (BaseModel):
    gear_type: str
    new_item: int
class Enter_Remove (BaseModel):
    remove_item: int
    gear_type: str
class Enter_Delete (BaseModel):
    delete_item: int