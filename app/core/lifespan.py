from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.core.log import logger

@asynccontextmanager
async def lifespan(app: FastAPI): 
    dw_mysql_client_manager.init_client()
    meta_mysql_client_manager.init_client()
    qdrant_client_manager.init_client()
    es_client_manager.init_client()
    embedding_client_manager.init_client()
    yield
    await dw_mysql_client_manager.close()
    await meta_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()