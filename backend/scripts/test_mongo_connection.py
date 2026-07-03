import asyncio
from app.db import db


async def main():
    result = await db.command("ping")
    print("Mongo connection successful! Response:", result)


if __name__ == "__main__":
    asyncio.run(main())