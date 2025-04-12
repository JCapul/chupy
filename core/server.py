import logging

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from core.context import ctx

logger = logging.getLogger(__name__)

DEFAULT_INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="title"></title>
    <script src="https://cdn.plot.ly/plotly-basic-3.0.1.min.js" charset="utf-8"></script>
    <script src="./static/main.js"></script>
    <script src="./static/ext-plotly.js"></script>
</head>

<body id="body" x-handler="__init" x-trigger="x:inited">
</body>

</html>
"""

# TODO: add CSRF middleware

class Server(Starlette):
    def __init__(self, component_factory, index_html=DEFAULT_INDEX_HTML):
        self._component_factory = component_factory
        self._index_html = index_html
        super().__init__(
            debug=True,
            routes=[
                Route("/", self.homepage),
                WebSocketRoute("/ws", self.websocket_endpoint),
                Mount("/static", app=StaticFiles(directory="static"), name="static"),
            ],
        )

    async def homepage(self, request):
        return HTMLResponse(self._index_html)

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        ctx.initialize(self._component_factory)
        async for msg in websocket.iter_json():
            updates = ctx.process_msg(msg)
            await websocket.send_json(updates)
        await websocket.close()

