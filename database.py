import os
from peewee import SqliteDatabase, Model, CharField, IntegerField
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_URL')
db = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    tg_username = CharField()
    tg_id = IntegerField(unique=True)


db.create_tables([User])
