from fastapi import APIRouter, WebSocket, Cookie
from typing import Optional, List
from rethinkdb import RethinkDB, asyncio_net
from starlette.websockets import WebSocketDisconnect
import db_pool
import asyncio
from json.decoder import JSONDecodeError
from threading import Thread
from utils import wrap_iter
from pydantic import BaseModel, validator, ValidationError
from datetime import date, datetime

r = RethinkDB()

router = APIRouter()

class MessageModel(BaseModel):
    text: str
    user: str

    @validator('text')
    def non_empty_validator(cls, value):
        if '' == value.strip():
            raise ValueError('Сообщение не должно быть пустым!')
        return value

async def post_message(message):
    async with db_pool.pool.connect() as conn:
        await (r.db('app').table('chat')
            .insert(message)
            .run(conn)
        )

async def message_feed(callback):
    async with db_pool.pool.connect() as conn:
        cursor = await (r.db('app').table('chat')
            .changes(include_initial=False)
            .run(conn)
        )
        async for message in cursor:
            await callback(message['new_val'])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.feed_init = False
        # asyncio.get_event_loop().create_task(message_feed(self.broadcast))

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

        if not self.feed_init:
            self.feed_init = True
            asyncio.get_event_loop().create_task(message_feed(self.broadcast))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.get('/chat/history')
async def get_history(limit: int = 20):
    limit = min(limit, 50)
    async with db_pool.pool.connect() as conn:
        cursor = await (r.db('app').table('chat')
            .order_by(index=r.desc('date'))
            .limit(limit)
            .run(conn)
        )
        messages = []
        async for row in cursor:
            messages.append(row)
        return messages

@router.websocket_route('/chat/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = MessageModel(**data)
                await post_message({
                    'user': message.user,
                    'message': message.text,
                    'date': datetime.now().timestamp()
                })
            except ValidationError as e:
                await manager.send_personal_message(
                    e.json(),
                    websocket
                )
            except JSONDecodeError:
                await manager.send_personal_message(
                    {
                        'user': 'Система',
                        'message': 'Не удалось декодировать сообщение',
                        'date': datetime.now().timestamp()
                    },
                    websocket
                )
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        


@router.post('/chat')
async def post_message_method(message: MessageModel):
    prepared_message = {
        'user': message.user,
        'message': message.text,
        'date': datetime.now().timestamp()
    }
    await post_message(prepared_message)
