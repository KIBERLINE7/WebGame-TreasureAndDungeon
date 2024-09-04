import uuid
import hashlib

from fastapi import APIRouter, Depends, Response, Cookie, Request
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import Enter_Data_Auth, Enter_Data_Registr
from src.database import get_async_session
from src.models import user, token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post('/logout')
async def logout (response: Response, request: Request , sessions: AsyncSession = Depends(get_async_session)):
    active_token = request.cookies.get('usertoken')
    response.delete_cookie('usertoken')
    stmt = delete(token).where(token.c.token==active_token)
    await sessions.execute(stmt)
    await sessions.commit()

    return {"status": "success"}

@router.post('/login')
async def entr_auth (enter_data: Enter_Data_Auth, response: Response, sessions: AsyncSession = Depends(get_async_session)):
    query = select(user).where(user.c.login == enter_data.login)
    result = await sessions.execute(query)
    get_user = result.one_or_none()

    if get_user != None:
        if enter_data.login != None and enter_data.password != None :
            hash_pass = enter_data.password.encode()
            hash_pass = hashlib.sha3_256(hash_pass).hexdigest()
            account_pass = get_user[2]

            if hash_pass == account_pass:
                uu = uuid.uuid1()
                response.set_cookie('usertoken', value=str(uu))
                create_token = {"token": str(uu), "user_id": get_user[0]}

                stmt_token = insert(token).values(**create_token)
                await sessions.execute(stmt_token)
                await sessions.commit()
                return {"status": "success"}

            else:
                return {"status": "failed"}

        else:
            return {"status": "incorrect"}
    else:
        return {"status": "empty"}

@router.post('/regist')
async def add_user (enter_data: Enter_Data_Registr, response: Response, sessions: AsyncSession = Depends(get_async_session)):
    query = select(user).where(user.c.login == enter_data.login)
    result = await sessions.execute(query)
    get_user = result.one_or_none()
    if get_user == None:
        if enter_data.login != None and enter_data.password != None :
            hash_pass = enter_data.password.encode()
            hash_pass = hashlib.sha3_256(hash_pass).hexdigest()
            enter_data.password = hash_pass

            enter = {
                "login": enter_data.login,
                "password": enter_data.password,
                "is_active":True
            }

            stmt = insert(user).values(**enter)
            await sessions.execute(stmt)
            await sessions.commit()

            query = select(user).where(user.c.login == enter_data.login)
            result = await sessions.execute(query)
            get_user = result.one_or_none()

            uu = uuid.uuid1()
            response.set_cookie('usertoken', value=str(uu))
            create_token = {"token": str(uu), "user_id": get_user[0]}

            stmt_token = insert(token).values(**create_token)
            await sessions.execute(stmt_token)
            await sessions.commit()

            return {"status": "success"}
        else :
            return {"status": "incorrect"}
    else :
        return {"status": "full"}
