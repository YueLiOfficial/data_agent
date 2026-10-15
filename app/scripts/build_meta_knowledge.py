import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.es.value_es_repository import ValueESRepoSitory
from app.repositories.qdrnt.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrnt.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.services.meta_knowledge_service import MetaKnowledgeService

from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.conf.meta_config import meta_config
from app.core.log import logger


async def main():
    es_client_manager.init_client()
    dw_mysql_client_manager.init_client()
    meta_mysql_client_manager.init_client()
    qdrant_client_manager.init_client()
    embedding_client_manager.init_client()

    try:
        async with (
            dw_mysql_client_manager.session_fectory() as dw_session, # type: ignore
            meta_mysql_client_manager.session_fectory() as meta_session # type: ignore
        ):  
            dw_session: AsyncSession
            meta_session: AsyncSession

            service = MetaKnowledgeService(
                value_es_repo=ValueESRepoSitory(es_client_manager.client), # type: ignore
                dw_mysql_repo=DWMysqlRepository(dw_session),
                meta_mysql_repo=MetaMysqlRepository(meta_session),
                column_qdrant_repo=ColumnQdrantRepository(qdrant_client_manager.client), # type: ignore
                metric_qdrant_repo=MetricQdrantRepository(qdrant_client_manager.client), # type: ignore
                embedding_client=embedding_client_manager.client, # type: ignore
            )

            await service.build(meta_config)

            await dw_session.commit()
            await meta_session.commit()

            logger.success(f"构建元数据库成功")

    except Exception as e:
        logger.error(f"构建元数据库失败: {str(e)}")
        await dw_session.rollback() # type: ignore
        await meta_session.rollback() # type: ignore
        raise
    finally:
        await es_client_manager.close()
        await dw_mysql_client_manager.close()
        await meta_mysql_client_manager.close()
        await qdrant_client_manager.close()

if __name__ == "__main__":
    asyncio.run(main())