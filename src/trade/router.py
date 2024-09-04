import uuid
import hashlib
import json
import random
from fastapi import APIRouter, Depends, Response, Cookie, Request
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.trade.schemas import *
from src.database import get_async_session
from src.models import user, token, gear, items, character, listbufs, listtypes
#--------------------------------------------------------------------
# This block contains methods related to the trader
#--------------------------------------------------------------------

character_tag = ["nickname", "level", "actual_xp", "xp_to_level", "wallet", "health", "attack_point", "defend"]
items_tag = ["id", "name", "is_equip", "buf", "type", "price"]

router = APIRouter(
    prefix="/trader",
    tags=["Trader"]
)

@router.get('/market')
async def render_page_market (request: Request , sessions: AsyncSession = Depends(get_async_session)):
    active_token = request.cookies.get('usertoken')
    query = select(token.c.user_id).where(token.c.token == active_token)
    result = await sessions.execute(query)
    active_user = result.one_or_none()

    if (active_user == None):
        return {"status": "fail_user"}

    query = select(character).where(character.c.user_id == active_user[0])
    result = await sessions.execute(query)
    active_chacter = result.one_or_none()

    if (active_chacter == None):
        return {"status": "fail_character"}

    map_character = dict()

    i = 1
    for elemnt in character_tag:
        if i == 2:
            i += 1
        map_character[elemnt] = active_chacter[i]
        i += 1

    query = select(items).where(items.c.character_id == active_chacter[0]).where(items.c.is_equip == False)
    result = await sessions.execute(query)
    character_invent = result.all()
    data_invent = []
    if character_invent != None:
        character_invent.reverse()

    #We will issue the player's inventory ----------------------------------------------------------------------------

    if (character_invent == None):
        data_invent.append(None)
    else:
        for glob in character_invent:
            map_items = dict()
            i = 0
            for elemnt in items_tag:
                if i == 2:
                    i += 1
                map_items[elemnt] = glob[i]
                i += 1
            st = map_items['type']
            path = "../static/image/"
            path = path + st + "1" + ".jpg"
            map_items['image'] = path
            data_invent.append(map_items)



    # Remove all items from the merchant to generate new ones

    stmt = delete(items).where(items.c.character_id == 5)
    await sessions.execute(stmt)
    await sessions.commit()

    # We will generate an assortment for the merchant ---------------------------------------------------------------

    query = select(listtypes)
    result = await sessions.execute(query)
    list_types = result.all()

    query = select(listbufs)
    result = await sessions.execute(query)
    list_bufs = result.all()


    for i in range(4):
        new_item = dict()
        list_of_type = list_types[random.randint(0, len(list_types) - 1)]

        new_item_tag = list_of_type[1]
        new_item["type"] = new_item_tag

        list_first_name = list_of_type[2]
        list_second_name = list_of_type[3]
        new_item_name = list_first_name[random.randint(0, len(list_first_name) - 1)] + " " + list_second_name[random.randint(0, len(list_second_name) - 1)]
        new_item["name"] = new_item_name


        list_of_item_price = list_of_type[4]

        final_pos_rate = random.randint(0, len(list_of_item_price) - 1)

        new_item_price = 0
        if final_pos_rate == 0:
            new_item_price = random.randint(1, list_of_item_price[final_pos_rate])
        else:
            new_item_price = random.randint(list_of_item_price[final_pos_rate - 1],
                                            list_of_item_price[final_pos_rate])

        new_item["price"] = new_item_price

        new_item["is_equip"] = False

        count_bufs = random.randint(1, 3)
        new_items_bufs = dict()

        for j in range(count_bufs):
            new_buf_item = list_bufs[random.randint(0, len(list_bufs) - 1)]

            new_name_buf = new_buf_item[1]
            list_of_rate_buf = new_buf_item[2]

            new_rate_buf = 0

            final_pos_rate = random.randint(0, len(list_of_rate_buf) - 1)

            if final_pos_rate == 0:
                new_rate_buf = random.randint(1, list_of_rate_buf[final_pos_rate])
            else:
                new_rate_buf = random.randint(list_of_rate_buf[final_pos_rate - 1],
                                                list_of_rate_buf[final_pos_rate])

            new_items_bufs[new_name_buf] = new_rate_buf

        new_item["buf"] = new_items_bufs
        new_item["character_id"] = 5

        stmt = insert(items).values(**new_item)
        await sessions.execute(stmt)
        await sessions.commit()

    #We will issue the merchant's inventory ----------------------------------------------------------------------
    query = select(items).where(items.c.character_id == 5)
    result = await sessions.execute(query)
    trade_invent = result.all()
    data_trade = []
    for glob in trade_invent:
        map_items = dict()
        i = 0
        for elemnt in items_tag:
            if i == 2:
                i += 1
            map_items[elemnt] = glob[i]
            i += 1
        st = map_items['type']
        path = "../static/image/"
        path = path + st + "1" + ".jpg"
        map_items['image'] = path
        data_trade.append(map_items)

    return {
        "status": "success",
        "character": map_character,
        "character_invent": data_invent,
        "trader_invent": data_trade
    }

@router.patch('/market/buy')
async def buy_item (buy_items: Buy_items ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
    active_token = request.cookies.get('usertoken')
    query = select(token.c.user_id).where(token.c.token == active_token)
    result = await sessions.execute(query)
    active_user = result.one_or_none()

    if (active_user == None):
        return {"status": "fail_user"}

    query = select(character).where(character.c.user_id == active_user[0])
    result = await sessions.execute(query)
    active_chacter = result.one_or_none()

    if (active_chacter == None):
        return {"status": "fail_character"}

    #Checking for the possibility of purchase and writing off funds

    query = select(items).where(items.c.id == buy_items.items_id)
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    if (query_list == None):
        return {"status": "Not_item"}

    price_item = query_list[6]
    having_character = query_list[2]

    if having_character == active_chacter[0]:
        return {"status": "You_have"}

    query = select(character.c.wallet).where(character.c.id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()
    wallet_character = query_list[0]

    if wallet_character - price_item >= 0 :

        # Reassign item
        stmt = update(items).where(items.c.id == buy_items.items_id).values(character_id=active_chacter[0])
        await sessions.execute(stmt)
        await sessions.commit()

        # Let's change the player's wallet
        new_wallet = wallet_character - price_item
        stmt = update(character).where(character.c.id == active_chacter[0]).values(wallet = new_wallet)
        await sessions.execute(stmt)
        await sessions.commit()

        return {"status": "success"}

    else:
        return {"status": "fail_buy"}

@router.patch('/market/sell')
async def sell_item (sell_items: Sell_items ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
    active_token = request.cookies.get('usertoken')
    query = select(token.c.user_id).where(token.c.token == active_token)
    result = await sessions.execute(query)
    active_user = result.one_or_none()

    if (active_user == None):
        return {"status": "fail_user"}

    query = select(character).where(character.c.user_id == active_user[0])
    result = await sessions.execute(query)
    active_chacter = result.one_or_none()

    if (active_chacter == None):
        return {"status": "fail_character"}

    #Checking for the possibility of sale and crediting funds

    query = select(items).where(items.c.id == sell_items.items_id)
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    if (query_list == None):
        return {"status": "Not_item"}

    price_item = query_list[6]
    having_character = query_list[2]

    if having_character != active_chacter[0] :
        return {"status": "Dont_have"}

    query = select(character.c.wallet).where(character.c.id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()
    wallet_character = query_list[0]

    # Reassign item
    stmt = update(items).where(items.c.id == sell_items.items_id).values(character_id=5)
    await sessions.execute(stmt)
    await sessions.commit()

    # Let's change the player's wallet
    new_wallet = wallet_character + price_item
    stmt = update(character).where(character.c.id == active_chacter[0]).values(wallet = new_wallet)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}