# standalone

from app import app
from aiohttp import web

web.run_app(app, port=8886)
