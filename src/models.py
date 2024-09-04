from datetime import datetime

from sqlalchemy import MetaData, Boolean, TIMESTAMP, JSON, Table, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

metadata = MetaData()

# User table in Data base
user = Table(

    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("login", String, nullable=False),
    Column("password", String, nullable=False),
    Column("resitred_date", TIMESTAMP, default=datetime.utcnow),
    Column("is_active", Boolean, default=False, nullable=False)
)

# Unique token table in Data base
token = Table(

    "token",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("token", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"))

)

# User character table in Data base
character = Table(

    "character",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nickname", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("level", Integer, nullable=False, default=1),
    Column("actual_xp", Integer, default=0),
    Column("xp_to_level", Integer, nullable=False, default=10),
    Column("wallet", Integer, nullable=False, default=0),
    Column("health", Integer, nullable=False, default=100),
    Column("attack_point", Integer, nullable=False, default=1),
    Column("defend", Integer, nullable=False, default=0)
)

# Сharacter stats table
characteristics = Table(

    "characteristics",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("array_charac", JSON, nullable=False),
    Column("character_id", Integer, ForeignKey("character.id"))
)

# Table storing the inventory of characters
items = Table(

    "items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("character_id", Integer, ForeignKey("character.id")),
    Column("is_equip", Boolean, nullable=False, default=False),
    Column("buf", JSON, nullable=True),
    Column("type", String, nullable=False),
    Column("price", Integer, nullable=False, default=1)
)

# Table storing active equipment of characters
gear = Table(

    "gear",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("character_id", Integer, ForeignKey("character.id")),
    Column("helm", Integer, ForeignKey("items.id"), nullable=True),
    Column("chest", Integer, ForeignKey("items.id"), nullable=True),
    Column("legs", Integer, ForeignKey("items.id"), nullable=True),
    Column("arm", Integer, ForeignKey("items.id"), nullable=True),
    Column("weapon_1", Integer, ForeignKey("items.id"), nullable=True),
    Column("weapon_2", Integer, ForeignKey("items.id"), nullable=True),
    Column("amulet", Integer, ForeignKey("items.id"), nullable=True),
    Column("ring_1", Integer, ForeignKey("items.id"), nullable=True),
    Column("ring_2", Integer, ForeignKey("items.id"), nullable=True)

)

# Table of active sessions (dungeons)
session = Table(

    "session",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("character_id", Integer, ForeignKey("character.id")),
    Column("difficult", Integer, nullable=False)

)

# Table of all possible enemies in the game
enemylist = Table(

    "enemylist",
    metadata,
Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("health", Integer, nullable=False),
    Column("attack_point", Integer, nullable=False),
    Column("defend", Integer, nullable=False),
    Column("xp", Integer)

)

# Table of enemies active in sessions
enemy = Table(

    "enemy",
    metadata,
Column("id", Integer, primary_key=True, autoincrement=True),
    Column("session_id", Integer, ForeignKey("session.id")),
    Column("name", String, nullable=False),
    Column("health", Integer, nullable=False),
    Column("attack_point", Integer, nullable=False),
    Column("defend", Integer, nullable=False),
    Column("xp", Integer)

)

# Table of all possible buffs for equipment
listbufs = Table(

    "listbufs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("ratebufs", ARRAY(Integer))

)

# Table for generating items
listtypes = Table(

    "listtypes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String),
    Column("firstname", ARRAY(String)),
    Column("secondname", ARRAY(String)),
    Column("rateprice", ARRAY(Integer))

)