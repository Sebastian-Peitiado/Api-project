import os
from typing import Collection
from fastapi import Depends
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client() -> MongoClient:
    host = os.environ["DB_HOST"]
    port = int(os.environ["DB_PORT"])
    user = os.environ["DB_USERNAME"]
    password = os.environ["DB_PASSWORD"]

    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    return MongoClient(uri, serverSelectionTimeoutMS=3000)


def get_usuarios_collection() -> Collection:
    db_name = os.getenv("DB_TEST_NAME") if os.getenv("PYTHON_ENV") == "test" else os.getenv("DB_NAME")
    client = get_mongo_client()
    return client[db_name]["usuarios"]


def insert_user_in_collection(user,collection = None):
    if collection is None:
        collection = get_usuarios_collection()
    result = collection.insert_one(user.model_dump())
    return result