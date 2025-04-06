import json
import sys
import os

from pymongo import MongoClient

docker_db = os.environ.get('DOCKER_DB', "false")

if docker_db == "true":
    print("using docker compose db")
    mongo_client = MongoClient("mongo")
else:
    print("using local db")
    mongo_client = MongoClient("localhost")

db = mongo_client["cse312"]

chat_collection = db["chat"]

user_collection = db["users"]

account_collection = db["accounts"]

oauth_collection = db["oauth_accounts"]

video_collection = db["videos"]


if __name__ == '__main__':
    chat_collection.delete_many({})
    user_collection.delete_many({})
    video_collection.delete_many({})