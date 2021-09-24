import asyncio
import json
from aiohttp import web
import datetime
from json import JSONEncoder

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

class Clipboard(object):
    MAX_HISTORY_SIZE = 5
    ENTRY_EXPIRATION_SPAN_IN_SEC = 5*60

    def __init__(self):
        self._history = []
        self._update_event = asyncio.Event()
        self._taks = None

    def start(self):
        self._taks = asyncio.create_task(self._run())

    async def _run(self):
        while True:
            await asyncio.sleep(1)
            if len(self._history) > 0 and self._history[-1]['expiration_time'] < datetime.datetime.now():
                print(f'Clipboard: expired: {self._history[-1]["content"]}')
                self._history = self._history[:-1]
                self._update_event.set()


    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        print("Clipboard: Open websocket")
        while not ws.closed:
            try:
                await asyncio.wait_for(self._update_event.wait(), timeout=5)
                self._update_event.clear()
            except asyncio.TimeoutError as ex:
                pass
            await ws.send_str(json.dumps(self._history, cls=DateTimeEncoder))

        print('Clipboard: websocket connection closed')
        return ws

    async def add(self, request):
        data = await request.json()
        if 'newEntry' in data:
            newEntry = data['newEntry']
            print(f'Clipboard: add: {newEntry}')
            self._add_to_history(newEntry)
            self._update_event.set()
        return web.Response()
    
    def _add_to_history(self, new_entry_content):
        new_entry = dict()
        new_entry['content'] = new_entry_content
        new_entry['expiration_time'] = datetime.datetime.now() + datetime.timedelta(seconds=Clipboard.ENTRY_EXPIRATION_SPAN_IN_SEC)
        self._history.insert(0, new_entry)
        if len(self._history) > Clipboard.MAX_HISTORY_SIZE:
            self._history = self._history[:Clipboard.MAX_HISTORY_SIZE]

    async def clear_history(self, request):
        self._history = []
        self._update_event.set()
        return web.Response()
    
    async def apply_entry(self, request):
        data = await request.json()
        if 'applyEntry' in data:
            index = data['applyEntry']
            if index > 0 and index < len(self._history):
                print(f'Clipboard: apply: {index}')
                entry = self._history[index]
                del self._history[index]
                self._add_to_history(entry['content'])
                self._update_event.set()
        return web.Response()
    
    async def clear_entry(self, request):
        data = await request.json()
        if 'clearEntry' in data:
            index = data['clearEntry']
            if index > 0 and index < len(self._history):
                print(f'Clipboard: clear: {index}')
                del self._history[index]
                self._update_event.set()
        return web.Response()
    