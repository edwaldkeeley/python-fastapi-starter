from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db_init import init_db_schema

from app.api.v1.api_v1 import api_router
from app.migrations.run import run_migrations


async def lifespan(app: FastAPI):
    # Startup
    await run_migrations()
    await init_db_schema()
    yield
    # Shutdown (if needed, close DB pool here)


app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")
