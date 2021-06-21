import os
import sys
from async_repool import AsyncConnectionPool
from rethinkdb import RethinkDB

this = sys.modules[__name__]
this.pool = None

r = RethinkDB()

async def init_pool():
    password = os.environ.get('RETHINKDB_PASSWORD')
    this.pool = AsyncConnectionPool({
        'host': 'db',
        'password': password
    },
    pool_size=50
    )
    await this.pool.init_pool()

async def init_tables():
    async with this.pool.connect() as conn:
        if 'app' not in await r.db_list().run(conn):
            await r.db_create('app').run(conn)
        
        conn.use('app')
        
        tables = await r.table_list().run(conn)
        required_tables = [
            (
                'chat', 
                {'primary_key': 'date'}
            ),
            (
                'rooms',
                {}
            )
        ]
        
        for table_spec in required_tables:
            if table_spec[0] not in tables:
                await r.table_create(table_spec[0], **table_spec[1]).run(conn)

