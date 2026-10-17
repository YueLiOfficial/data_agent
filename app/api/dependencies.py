from fastapi import Depends

from app.repositories.qdrnt.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrnt.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.es.value_es_repository import ValueESRepoSitory
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.clients.es_client_manager import es_client_manager
from app.services.query_service import QueryService

from sqlalchemy.ext.asyncio import AsyncSession

async def get_dw_session():
    async with dw_mysql_client_manager.session_fectory() as session: # type: ignore
        yield session

async def get_meta_session():
    async with meta_mysql_client_manager.session_fectory() as session: # type: ignore
        yield session

def get_query_service(
    dw_session: AsyncSession=Depends(get_dw_session),
    meta_session: AsyncSession=Depends(get_meta_session)
) -> QueryService:
    return QueryService(
        value_es_repo=ValueESRepoSitory(es_client_manager.client), # type: ignore
        dw_mysql_repo=DWMysqlRepository(dw_session),
        meta_mysql_repo=MetaMysqlRepository(meta_session),
        column_qdrant_repo=ColumnQdrantRepository(qdrant_client_manager.client), # type: ignore
        metric_qdrant_repo=MetricQdrantRepository(qdrant_client_manager.client), # type: ignore
        embedding_client=embedding_client_manager.client # type: ignore
    )