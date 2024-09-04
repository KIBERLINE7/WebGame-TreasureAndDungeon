import uuid
import hashlib
import json
import random
from fastapi import APIRouter, Depends, Response, Cookie, Request
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.invetr.schemas import *
from src.database import get_async_session
from src.models import user, token, gear, items, character, characteristics, session, enemylist, enemy

#-----------------------------------------------------------------------
# In this block are located methods that are active when the player is at the base
#-----------------------------------------------------------------------

character_tag = ["nickname", "level", "actual_xp", "xp_to_level", "wallet", "health", "attack_point", "defend"]
gear_tag = ["helm", "chest", "legs", "arm", "weapon_1", "weapon_2", "amulet", "ring_1", "ring_2"]
items_tag = ["id", "name", "is_equip", "buf", "type", "price"]
enemy_tags = ["session_id", "name", "health", "attack_point", "defend", "xp"]

router = APIRouter(
    prefix="/character",
    tags=["Charact"]
)

@router.post('/create')
async def create_character (enter_nick: Enter_Nick, request: Request , sessions: AsyncSession = Depends(get_async_session)):
    active_token = request.cookies.get('usertoken')
    query = select(token.c.user_id).where(token.c.token == active_token)
    result = await sessions.execute(query)
    active_user = result.one_or_none()

    if (active_user == None):
        return {"status": "fail_user"}

    query = select(character).where(character.c.user_id == active_user[0])
    result = await sessions.execute(query)
    active_chacter = result.one_or_none()

    if (active_chacter != None):
        return {"status": "detect_charater"}

    query = select(character).where(character.c.nickname == enter_nick.nickname)
    result = await sessions.execute(query)
    get_nick = result.one_or_none()

    if (get_nick != None):
        return {"status": "nick_reserve"}

    create_character = {"nickname": enter_nick.nickname, "user_id": active_user[0]}

    stmt = insert(character).values(**create_character)
    await sessions.execute(stmt)
    await sessions.commit()

    query = select(character.c.id).where(character.c.user_id == active_user[0])
    result = await sessions.execute(query)
    get_character_id = result.one_or_none()

    create_gear = {"character_id": get_character_id[0]}

    stmt = insert(gear).values(**create_gear)
    await sessions.execute(stmt)
    await sessions.commit()

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

    characteristic_list = dict()
    characteristic_list["nickname"] = map_character["nickname"]
    characteristic_list["health"] = map_character["health"]
    characteristic_list["attack_point"] = map_character["attack_point"]
    characteristic_list["defend"] = map_character["defend"]

    create_characteristic = {"array_charac": characteristic_list, "character_id": get_character_id[0]}

    stmt = insert(characteristics).values(**create_characteristic)
    await sessions.execute(stmt)
    await sessions.commit()


    return {"status": "success"}

@router.post('/select')
async def select_character (request: Request , sessions: AsyncSession = Depends(get_async_session)):
    return 0

@router.get('/inventory')
async def render_page_inventory (request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    query = select(gear).where(gear.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    character_gear = result.one_or_none()

    map_gear = dict()
    i = 2
    for elemnt in gear_tag:

        query = select(items).where(items.c.id == character_gear[i])
        result = await sessions.execute(query)
        item = result.one_or_none()

        map_item_gear = dict()
        if item == None:

            if elemnt == "ring_1" or elemnt == "ring_2" :
                map_gear[elemnt] = {"type": "ring"}
            elif elemnt == "weapon_1" or elemnt == "weapon_2" :
                map_gear[elemnt] = {"type": "weapon"}
            else:
                map_gear[elemnt] = {"type": elemnt}
        else:
            j = 0
            for elemnt_item in items_tag:
                if j == 2:
                    j += 1
                map_item_gear[elemnt_item] = item[j]
                j += 1

            st = map_item_gear['type']
            path = "../static/image/"
            path = path + st + "1" + ".jpg"
            map_item_gear['image'] = path
            map_gear[elemnt] = map_item_gear
        i += 1

    query = select(items).where(items.c.character_id == active_chacter[0]).where(items.c.is_equip == False)
    result = await sessions.execute(query)
    character_invent = result.all()

    data_inv = []

    if character_invent != None:
        character_invent.reverse()

    if (character_invent == None):
        data_inv.append(None)
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
            data_inv.append(map_items)

    return {
        "status": "success",
        "character": map_character,
        "list_gear": map_gear,
        "inventory": data_inv
    }

# Method for sap items in inventory
@router.patch('/inventory/swap')
async def swap_items (swap_items: Enter_Swap ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    stmt = update(items).where(items.c.id == swap_items.new_item).values(is_equip=True)
    await sessions.execute(stmt)
    await sessions.commit()

    swap_items_id = 0

    query = select(gear).where(gear.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.all()

    gear_list = query_list[0]
    print(query_list)

    i = 2
    map_gear = dict()
    for elemnt in gear_tag:
        if (gear_list[i] == None):
            map_gear[elemnt] = 0
        else:
            map_gear[elemnt] = gear_list[i]
        i += 1

    swap_items_id = map_gear[swap_items.gear_type]

    if swap_items_id != 0:
        stmt = update(items).where(items.c.id == swap_items_id).values(is_equip=False)
        await sessions.execute(stmt)
        await sessions.commit()

    swap = dict()
    swap[swap_items.gear_type] = swap_items.new_item
    stmt = update(gear).where(gear.c.character_id == active_chacter[0]).values(**swap)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}

# Method for remove on active item to inventory
@router.patch('/inventory/remove')
async def remove_items (remove_items: Enter_Remove ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    stmt = update(items).where(items.c.id == remove_items.remove_item).values(is_equip=False)
    await sessions.execute(stmt)
    await sessions.commit()

    remove = dict()
    remove[remove_items.gear_type] = None
    stmt = update(gear).where(gear.c.character_id == active_chacter[0]).values(**remove)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}

@router.patch('/inventory/delete')
async def delete_items (delete_items: Enter_Delete ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    stmt = delete(items).where(items.c.id == delete_items.delete_item)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}

@router.patch('/inventory/levelup')
async def level_up (request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    if map_character["actual_xp"] >= map_character["xp_to_level"]:
        map_character["level"] = map_character["level"] + 1
        map_character["actual_xp"] = map_character["actual_xp"] - map_character["xp_to_level"]
        map_character["xp_to_level"] = map_character["xp_to_level"] * 2
        map_character["health"] = map_character["health"] + 10
        map_character["attack_point"] = map_character["attack_point"] + 2
        map_character["defend"] = map_character["defend"] + 1
    else:
        return {"status": "fail_up"}

    stmt = update(character).where(character.c.id == active_chacter[0]).values(**map_character)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}

# Method for start dungeon session
@router.patch('/inventory/todungeon')
async def to_dungeon (request: Request , sessions: AsyncSession = Depends(get_async_session)):
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
    # Get character data
    map_character = dict()
    i = 1
    for elemnt in character_tag:
        if i == 2:
            i += 1
        map_character[elemnt] = active_chacter[i]
        i += 1

    # Get data on a character's equipment
    query = select(items).where(items.c.character_id == active_chacter[0]).where(items.c.is_equip == True)
    result = await sessions.execute(query)
    character_invent = result.all()

    # Let's prepare a new list of characteristics
    characteristic_list = dict()
    characteristic_list["nickname"] = map_character["nickname"]
    characteristic_list["health"] = map_character["health"]
    characteristic_list["attack_point"] = map_character["attack_point"]
    characteristic_list["defend"] = map_character["defend"]

    for element in character_invent:
        bufs = element[4]
        if bufs != None:
            for key in bufs:
                characteristic_list[key] += bufs[key]

    create_characteristic = {"array_charac": characteristic_list}
    # Let's update the character's cast
    stmt = update(characteristics).where(characteristics.c.character_id == active_chacter[0]).values(**create_characteristic)
    await sessions.execute(stmt)
    await sessions.commit()

    # Let's create a session and opponents to it
    difficl = random.randint(1, 5)
    create_session = {"character_id": active_chacter[0] , "difficult": difficl}

    stmt = insert(session).values(**create_session)
    await sessions.execute(stmt)
    await sessions.commit()
    # Let's get the created session for the key
    query = select(session).where(session.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    now_session = result.one_or_none()
    #Let's get a list of possible opponents
    query = select(enemylist)
    result = await sessions.execute(query)
    Enemy_List = result.all()
    # Let's form a pool of enemies for the dungeon
    for i in range(0, difficl):
        now_enemy = dict()
        chose = random.randint(0, len(Enemy_List) - 1)
        form_enemy = Enemy_List[chose]
        j = 1
        for tag in enemy_tags:
            if tag == "session_id":
                now_enemy[tag] = now_session[0]
            else:
                now_enemy[tag] = form_enemy[j]
                j += 1
        stmt = insert(enemy).values(**now_enemy)
        await sessions.execute(stmt)
        await sessions.commit()

    return {"status": "success"}