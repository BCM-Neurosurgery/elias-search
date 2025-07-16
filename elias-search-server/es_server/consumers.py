import json
from channels.generic.websocket import AsyncWebsocketConsumer
from code import InteractiveConsole
import io, sys

class QueryProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"progress_{self.session_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_progress(self, event):
        await self.send(text_data=json.dumps(event["message"]))
        
        
class DjangoShellConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_superuser:
            await self.close()
            return
        self.console = InteractiveConsole()
        await self.accept()
    
    async def receive(self, text_data):
        buffer = io.StringIO()
        sys.stdout = buffer
        sys.stderr = buffer
        try:
            self.console.push(text_data)
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        await self.send(buffer.getvalue())