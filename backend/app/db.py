"""MongoDB connection for Vrika Admin."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings


class Mongo:
    client: AsyncIOMotorClient | None = None


mongo = Mongo()


async def get_database() -> AsyncIOMotorDatabase:
    if mongo.client is None:
        raise RuntimeError("Database not initialized")
    settings = get_settings()
    return mongo.client[settings.mongodb_db]


async def init_db() -> None:
    settings = get_settings()
    mongo.client = AsyncIOMotorClient(settings.mongodb_uri)
    db = mongo.client[settings.mongodb_db]
    # Ensure indexes for license admin collections
    await db["license_customers"].create_index("email", unique=True)
    await db["license_activity"].create_index([("timestamp", -1)])
    await db["licenses"].create_index("customer_id")
    await db["licenses"].create_index("status")


async def close_db() -> None:
    if mongo.client:
        mongo.client.close()
        mongo.client = None
