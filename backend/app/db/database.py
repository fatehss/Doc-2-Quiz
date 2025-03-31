from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os

MONGO_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi('1'))
db = client[MONGODB_DATABASE]





