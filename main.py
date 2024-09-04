from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.auth.router import router as router_auth
from src.invetr.router import router as router_invent
from src.trade.router import router as router_trade
from src.dungeon.router import router as router_dungeon
from src.pages.router import router as router_pages

app = FastAPI(
    title="Treasure AND Dungeon"
)

app.mount("/static", StaticFiles(directory="src/static"), name= "static")

app.include_router(router_auth)
app.include_router(router_invent)
app.include_router(router_trade)
app.include_router(router_dungeon)
app.include_router(router_pages)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"],
    allow_headers = ["Access-Control-Allow-Methods", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin"]
)