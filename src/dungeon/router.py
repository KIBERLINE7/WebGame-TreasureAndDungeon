import uuid
import hashlib
import json
import random
from fastapi import APIRouter, Depends, Response, Cookie, Request
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dungeon.schemas import *
from src.database import get_async_session
from src.models import user, token, gear, items, character, listbufs, listtypes, enemy, enemylist, session, characteristics

character_tag = ["nickname", "level", "actual_xp", "xp_to_level", "wallet", "health", "attack_point", "defend"]
items_tag = ["id", "name", "is_equip", "buf", "type", "price"]
enemy_tags = ["id", "name", "health", "attack_point", "defend", "xp"]

router = APIRouter(
    prefix="/dungeon",
    tags=["Dungeon"]
)

# Used to generate a dungeon, perform a character attack and perform a character defense, generate received
# items for completing a dungeon, character escape from a dungeon

# query - query to select elements from the database
# stmt - request to change elements in the database

@router.get('/battle')
async def render_page_battle (request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    query = select(session).where(session.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    if query_list == None:
        return {"status": "fail_session"}

    now_session_id = query_list[0]

    # difficult - dungeon difficulty, the difficulty determines how much gold the character will lose
    # when dying and when leaving the dungeon
    difficult = query_list[2]


    # Let's form a character -----------------------------------------------------------------------

    map_character = dict()

    query = select(characteristics).where(characteristics.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    map_character = query_list[1]
    path = "../static/image/"
    path = path + "персонаж" + ".jpg"
    map_character['image'] = path

    #We will give away our opponents ----------------------------------------------------------------------
    query = select(enemy).where(enemy.c.session_id == now_session_id)
    result = await sessions.execute(query)
    all_enemy = result.all()
    data_enemy = []
    for glob in all_enemy:
        map_enemy = dict()
        i = 0
        for elemnt in enemy_tags:
            if i == 1:
                i += 1
            map_enemy[elemnt] = glob[i]
            i += 1
        st = map_enemy['name']
        path = "../static/image/"
        path = path + st + "1" + ".jpg"
        map_enemy['image'] = path
        data_enemy.append(map_enemy)

    return {
        "status": "success",
        "character": map_character,
        "enemy": data_enemy
    }

@router.patch('/battle/attack')
async def attack_character (attack_enemy: Attack_enemy ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    query = select(session).where(session.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    if query_list == None:
        return {"status": "fail_session"}

    now_session_id = query_list[0]
    difficult = query_list[2]

    # Получим персонажа ----------------------------------------------------------------------------------

    map_character = dict()

    query = select(characteristics).where(characteristics.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    map_character = query_list[1]

    # We will get an enemy to attack ----------------------------------------------------------------

    query = select(enemy).where(enemy.c.id == attack_enemy.enemy_id)
    result = await sessions.execute(query)
    attacking_enemy = result.one_or_none()

    if attacking_enemy == None:
        return {"status": "Enemy_not_found"}

    attacking_enemy_dict = dict()

    i = 0
    for tags in enemy_tags:
        if i == 1:
            i += 1
        attacking_enemy_dict[tags] = attacking_enemy[i]
        i += 1

    # Let's carry out an attack and calculate the enemy's HP

    character_attack = map_character["attack_point"]
    character_actual_xp = active_chacter[4]

    enemy_defend = attacking_enemy_dict["defend"]
    enemy_health = attacking_enemy_dict["health"]
    enemy_xp = attacking_enemy_dict["xp"]

    if character_attack > enemy_defend:
        enemy_health -= (character_attack - enemy_defend)
    else:
        enemy_health -= 1

    if enemy_health <= 0:
        stmt = delete(enemy).where(enemy.c.id == attacking_enemy_dict["id"])
        await sessions.execute(stmt)
        await sessions.commit()

        character_actual_xp += enemy_xp
        stmt = update(character).where(character.c.id == active_chacter[0]).values(actual_xp = character_actual_xp)
        await sessions.execute(stmt)
        await sessions.commit()



    else:
        stmt = update(enemy).where(enemy.c.id == attacking_enemy_dict["id"]).values(health = enemy_health)
        await sessions.execute(stmt)
        await sessions.commit()

    # We will check for enemies in the dungeon and if there are none, we will issue rewards----------------------------

    query = select(enemy).where(enemy.c.session_id == now_session_id)
    result = await sessions.execute(query)
    all_enemy = result.all()

    if len(all_enemy) == 0:

        stmt = delete(session).where(session.c.id == now_session_id)
        await sessions.execute(stmt)
        await sessions.commit()

        # Let's generate loot for the dungeon ---------------------------------------------------------------

        query = select(listtypes)
        result = await sessions.execute(query)
        list_types = result.all()

        query = select(listbufs)
        result = await sessions.execute(query)
        list_bufs = result.all()

        for i in range(difficult):
            new_item = dict()
            list_of_type = list_types[random.randint(0, len(list_types) - 1)]

            new_item_tag = list_of_type[1]
            new_item["type"] = new_item_tag

            list_first_name = list_of_type[2]
            list_second_name = list_of_type[3]
            new_item_name = list_first_name[random.randint(0, len(list_first_name) - 1)] + " " + list_second_name[
                random.randint(0, len(list_second_name) - 1)]
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
            new_item["character_id"] = active_chacter[0]

            stmt = insert(items).values(**new_item)
            await sessions.execute(stmt)
            await sessions.commit()

        return {"status": "finish"}
    else:
        return {"status": "next"}

@router.patch('/battle/defend')
async def defend_character (attack_enemy: Attack_enemy ,request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    query = select(session).where(session.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    if query_list == None:
        return {"status": "fail_session"}

    now_session_id = query_list[0]
    difficult = query_list[2]

    # Let's get a character ----------------------------------------------------------------------------------

    map_character = dict()

    query = select(characteristics).where(characteristics.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    map_character = query_list[1]

    # We'll get an enemy that attacks. ----------------------------------------------------------------

    query = select(enemy).where(enemy.c.id == attack_enemy.enemy_id)
    result = await sessions.execute(query)
    attacking_enemy = result.one_or_none()

    if attacking_enemy == None:
        return {"status": "Enemy_not_found"}

    attacking_enemy_dict = dict()

    i = 0
    for tags in enemy_tags:
        if i == 1:
            i += 1
        attacking_enemy_dict[tags] = attacking_enemy[i]
        i += 1

    # Let's carry out defense against attack and calculate the character's HP

    character_defend = map_character["defend"]
    character_actual_hp = map_character["health"]

    enemy_attack = attacking_enemy_dict["attack_point"]


    if character_defend == enemy_attack:
        character_actual_hp -= 1
    elif character_defend < enemy_attack :
        character_actual_hp -= (enemy_attack - character_defend)

    if character_actual_hp <= 0:
        stmt = delete(enemy).where(enemy.c.session_id == now_session_id)
        await sessions.execute(stmt)
        await sessions.commit()

        stmt = delete(session).where(session.c.id == now_session_id)
        await sessions.execute(stmt)
        await sessions.commit()

        stmt = update(character).where(character.c.id == active_chacter[0]).values(wallet = active_chacter[6] - difficult * 2)
        await sessions.execute(stmt)
        await sessions.commit()

        return {"status": "died"}

    else:
        map_character["health"] = character_actual_hp
        stmt = update(characteristics).where(characteristics.c.character_id == active_chacter[0]).values(array_charac = map_character)
        await sessions.execute(stmt)
        await sessions.commit()

        return {"status": "damageOK"}

# Method for leave on dungeon
@router.patch('/battle/leave')
async def leave_character (request: Request , sessions: AsyncSession = Depends(get_async_session)):
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

    query = select(session).where(session.c.character_id == active_chacter[0])
    result = await sessions.execute(query)
    query_list = result.one_or_none()

    if query_list == None:
        return {"status": "fail_session"}

    now_session_id = query_list[0]
    difficult = query_list[2]


    stmt = delete(enemy).where(enemy.c.session_id == now_session_id)
    await sessions.execute(stmt)
    await sessions.commit()

    stmt = delete(session).where(session.c.id == now_session_id)
    await sessions.execute(stmt)
    await sessions.commit()

    stmt = update(character).where(character.c.id == active_chacter[0]).values(wallet = active_chacter[6] - difficult)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}


