from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field #Validierung & Typensicherheit
from enum import Enum #Enumerationen
from jose import jwt
from typing import Optional
#Daten
#-----------------------------------------------------------------
items = [
    {"name": "Computer", "preis": 1000, "typ":"hardware"},
    {"name": "Monitor", "preis": 500, "typ":"hardware"},
    {"name": "Spiel", "preis": 50, "typ":"software"},
    {"name": "Windwows", "preis": 90, "typ":"software"} 
]


#--Definitionen 
#---------------------------------------------------------------
#Enumeration
class Type(Enum):
    hardware = "hardware"
    software = "software"

# pydantic
class Item(BaseModel):
    name: str
    preis: int = Field(100, gt=0, lt=2500)
    typ: Type

#definiert die Rückgabe
class ResponseItem(BaseModel):
    name: str
    typ: Type

app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

#security
@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if data.username == "test" and data.password == "test":
        access_token = jwt.encode({"user:": data.username}, key="secret")
        return {"access_token":access_token, "token_type":"bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Incorrect username or password", 
        headers={"WWW-Authenticate":"Bearer"}
    )


# API Funktionen
#---------------------------------------------------------------
@app.get("/")
async def hello():
    return {"message": "Hello World"}

@app.get("/items/")
async def get_Items( token:str = Depends(oauth2_schema), q:Optional[str] = None): #Token wird an die Funktion mitgegeben
    if q: 
        data=[]
        for item in items:
            if item.get("typ") == q:
                data.append(item)
        return data
    else: 
        return items

@app.get("/items/{item_id}",dependencies=[Depends(oauth2_schema)])
async def get_Item(item_id: int):
    return items[item_id]

@app.post("/items/", response_model=ResponseItem,dependencies=[Depends(oauth2_schema)])
async def create_item(data: Item):
    items.append(data)
    return data

@app.put("/items/{item_id}",dependencies=[Depends(oauth2_schema)])
async def change_item(item_id: int, item:Item):
    items[item_id] = item
    return item


@app.delete("/items/{item_id}",dependencies=[Depends(oauth2_schema)])
async def delete_item(item_id: int ):
    item = items[item_id]
    items.pop(item_id)
    return {"deleted":item}