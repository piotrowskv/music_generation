import asyncio

from hypercorn.asyncio import serve
from hypercorn.config import Config

from app import app

config = Config()
config.bind = ["127.0.0.1:8000"]

asyncio.run(serve(app.app, config))  # type: ignore
