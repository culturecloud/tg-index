import asyncio
import uvloop
import pathlib
import logging

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.telegram import Client
from app.routes import setup_routes
from app.views import Views, middleware_factory
from app.config import (
    debug,
    host,
    port,
    session_string,
    api_id,
    api_hash,
    authenticated,
    username,
    password,
    SESSION_COOKIE_LIFETIME,
    SECRET_KEY,
)

logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
logging.getLogger("telethon").setLevel(logging.INFO if debug else logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.INFO if debug else logging.ERROR)

log = logging.getLogger(__name__)

class Indexer:

    TEMPLATES_ROOT = pathlib.Path(__file__).parent / "templates"

    def __init__(self):
        middlewares = []
        if authenticated:
            middlewares.append(
                session_middleware(
                    EncryptedCookieStorage(
                        secret_key=SECRET_KEY.encode(),
                        max_age=60 * SESSION_COOKIE_LIFETIME,
                        cookie_name="TG_INDEX_SESSION",
                        secure=True,
                    )
                )
            )

        middlewares.append(middleware_factory())
        self.loop = uvloop.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.server = web.Application(middlewares=middlewares)

        self.server.on_startup.append(self.startup)
        self.server.on_cleanup.append(self.cleanup)

        self.tg_client = Client(session_string, api_id, api_hash)

        self.server["is_authenticated"] = authenticated
        self.server["username"] = username
        self.server["password"] = password

    async def startup(self, server: web.Application):
        await self.tg_client.start()
        log.debug("telegram client started!")

        await setup_routes(server, Views(self.tg_client))

        loader = jinja2.FileSystemLoader(str(self.TEMPLATES_ROOT))
        aiohttp_jinja2.setup(server, loader=loader)

    async def cleanup(self, server: web.Application):
        await self.tg_client.disconnect()
        log.debug("telegram client disconnected!")

    def run(self):
        web.run_app(self.server, host=host, port=port, loop=self.loop)

Indexer().run()
