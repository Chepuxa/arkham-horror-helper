from fastapi import FastAPI, Depends, HTTPException, Path, Query, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import db_pool
from chat import chat as chat_methods
from room import methods as room_methods

app = FastAPI()
app.include_router(chat_methods.router)
app.include_router(room_methods.router)

@app.on_event('startup')
async def startup_event():
    await db_pool.init_pool()
    await db_pool.init_tables()

@app.on_event('shutdown')
async def shutdown_event():
    await db_pool.pool.release_pool()

@app.get('/')
async def root():
    return {"message": "Hello, world!"}
