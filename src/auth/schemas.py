from pydantic import BaseModel

class Enter_Data_Auth (BaseModel):
    login : str
    password :str

class Enter_Data_Registr (BaseModel):
    login: str
    password: str