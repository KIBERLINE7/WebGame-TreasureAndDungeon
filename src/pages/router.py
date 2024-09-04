from fastapi import Request, Response, APIRouter, Depends
from fastapi.templating import Jinja2Templates

from src.trade.router import render_page_market, buy_item, sell_item
from src.invetr.router import render_page_inventory, remove_items, swap_items, delete_items, create_character, level_up, to_dungeon
from src.auth.router import logout, entr_auth, add_user
from src.dungeon.router import render_page_battle, attack_character, defend_character

router = APIRouter(
    prefix = "/pages",
    tags = ["Pages"]
)

templates = Jinja2Templates(directory="src/templates")

@router.get("/auth")
def get_auth_page (request: Request):
    return templates.TemplateResponse("authoriz.html", {"request": request})

@router.get("/registr")
def get_registr_page (request: Request):
    return templates.TemplateResponse("registr.html", {"request": request})

@router.get("/create")
def get_create_character_page(request: Request):
    return templates.TemplateResponse("CreateCharacter.html", {"request": request})

@router.get("/inventory")
def get_inventory_page (request: Request, operatons = Depends(render_page_inventory)):
    if operatons["status"] != "success":
        return templates.TemplateResponse("inventory.html", {"request": request, "operations": operatons["status"]})
    else:
        return templates.TemplateResponse("inventory.html", {"request": request,
                                                                    "operations": [operatons["character"],
                                                                                   operatons["list_gear"],
                                                                                   operatons["inventory"]]    })

@router.get("/dungeon")
def get_dungeon_page (request: Request, operatons = Depends(render_page_battle)):
    if operatons["status"] != "success":
        return templates.TemplateResponse("dungeon.html", {"request": request, "operations": operatons["status"]})
    else:
        return templates.TemplateResponse("dungeon.html", {"request": request,
                                                                    "operations": [operatons["character"],
                                                                                   operatons["enemy"]]    })

@router.get("/trade")
def get_trade_page (request: Request, operatons = Depends(render_page_market)):
    if operatons["status"] != "success":
        return templates.TemplateResponse("trade.html", {"request": request, "operations": operatons["status"]})
    else:
        return templates.TemplateResponse("trade.html", {"request": request,
                                                                    "operations": [operatons["character"],
                                                                                   operatons["character_invent"],
                                                                                   operatons["trader_invent"]]    })