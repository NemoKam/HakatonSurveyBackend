import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import config
from .api.routes import router as api_router
from .database import sessionmanager


sessionmanager.create_tables()

app = FastAPI(
    title=config.PROJECT_TITLE,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")

# app.mount("/static", StaticFiles(directory="fastapp/static"), name="static")