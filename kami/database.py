from datetime import datetime

from peewee import BooleanField, DateTimeField, IntegerField, SqliteDatabase, Model, TextField


db = SqliteDatabase("kami.db", pragmas={
    "journal_mode": "wal",
    "cache_size": -1 * 64000,
    "foreign_keys": 1,
    "synchronous": 1
})

class Anime(Model):
    class Meta:
        database = db

    name = TextField(unique=True, default="")
    fansub_id = IntegerField(default="")
    url = TextField(default="")
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)


class Fansub(Model):
    class Meta:
        database = db

    name = TextField(unique=True, default="")


class Users(Model):
    class Meta:
        database = db

    username = TextField(unique=True, default="")
    password = TextField(default="")
    is_admin = BooleanField(default=False)
    is_twofa = BooleanField(default=False)
    twofa_secret = TextField(default="")


class UsersSessions(Model):
    class Meta:
        database = db
        table_name = "users_sessions"

    user_id = IntegerField(default="")
    jwt_token = TextField(default="")


MODELS = [
    Anime,
    Users,
    UsersSessions,
    Fansub
]