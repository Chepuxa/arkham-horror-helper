from fastapi import APIRouter, WebSocket, Cookie, Path
from starlette.websockets import WebSocketDisconnect
from pydantic import ValidationError
from rethinkdb import RethinkDB
import asyncio

r = RethinkDB()
router = APIRouter()

import db_pool
from room.room import CharacterModel, RoomParamsModel, ChangeModel, Room


async def load_room(id: int, db_conn):
    room_obj = await (r.db('app').table('rooms')
        .get(id)
        .run(db_conn)
    )
    return Room.from_dict(room_obj)


async def save_room(room: Room, db_conn):
    room_obj = room.to_dict()
    return await (r.db('app').table('rooms')
        .get(room.id)
        .update(room_obj)
        .run(db_conn)
    ), room_obj


@router.post('/room/make')
async def api_make_room(params: RoomParamsModel):
    try:
        room = Room.from_params(params)
        obj = room.to_dict()
        async with db_pool.pool.connect() as conn:
            results = await (r.db('app').table('rooms')
                .insert(obj)
                .run(conn)
            )
        if results['inserted'] > 0:
            return obj
        else:
            raise RuntimeError
    finally:
        pass


@router.get('/room/complete')
async def api_get_complete_rooms():
    limit = 20
    async with db_pool.pool.connect() as conn:
        cursor = await (r.db('app').table('rooms')
            .filter({'complete': True})
            .order_by(r.desc('start_date'))
            .limit(limit)
            .run(conn)
        )
        return cursor


@router.get('/room/{id}')
async def api_get_room(id: int = Path(...)):
    try:
        async with db_pool.pool.connect() as conn:
            room = await load_room(id, conn)
            return room.to_dict()
    finally:
        pass


@router.post('/room/{id}')
async def make_change(change: ChangeModel, id: int = Path(...)):
    return await apply_change(id, change)


async def apply_change(room_id, change: ChangeModel):
    async with db_pool.pool.connect() as conn:
        room = await load_room(room_id, conn)

        success = room.make_change(change.who, change.what, change.where, change.extra)
        if success:
            results, room_obj = await save_room(room, conn)
            return room_obj
        else:
            return None

async def message_feed(room_id, callback):
    async with db_pool.pool.connect() as conn:
        cursor = await (r.db('app').table('rooms').get(room_id)
            .changes(include_initial=False)
            .run(conn)
        )
        async for message in cursor:
            keep_alive = await callback(message['new_val'])           
            if not keep_alive:
                return

class RoomManager:
    def __init__(self, room_id):
        self.room_id = room_id
        self.users = []
        self.feed_init = False
        self.dying = False
        # asyncio.get_event_loop().create_task(message_feed(self.broadcast))

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.users.append(websocket)

        if not self.feed_init:
            self.feed_init = True
            asyncio.get_event_loop().create_task(message_feed(self.room_id, self.breakable_broadcast))

    def disconnect(self, websocket: WebSocket):
        self.users.remove(websocket)
        if len(self.users) == 0:
            self.dying = True

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def breakable_broadcast(self, message):
        if self.dying:
            return False

        for user in self.users:
            await user.send_json(message)

        return True

    async def broadcast(self, message):
        for user in self.users:
            await user.send_json(message)

rooms = {}

@router.websocket('/room/{id}/ws')
async def websocket_endpoint(websocket: WebSocket, id: int):
    if id in rooms:
        manager = rooms[id]
    else:
        rooms[id] = manager = RoomManager(id)
    
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                change = ChangeModel(**data)
                success = await apply_change(
                    id, change
                )
            except ValidationError as e:
                await manager.send_personal_message(
                    e.json(),
                    websocket
                )
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)