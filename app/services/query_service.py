import json

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger
from app.agent.graph import graph

from app.repositories.es.value_es_repository import ValueESRepoSitory
from app.repositories.qdrnt.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrnt.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository

class QueryService:
    def __init__(
        self,
        value_es_repo: ValueESRepoSitory,
        dw_mysql_repo: DWMysqlRepository,
        meta_mysql_repo: MetaMysqlRepository,
        column_qdrant_repo: ColumnQdrantRepository,
        metric_qdrant_repo: MetricQdrantRepository,
        embedding_client: HuggingFaceEndpointEmbeddings,
    ) -> None:
        self.value_es_repo = value_es_repo
        self.dw_mysql_repo = dw_mysql_repo
        self.meta_mysql_repo = meta_mysql_repo
        self.column_qdrant_repo = column_qdrant_repo
        self.metric_qdrant_repo = metric_qdrant_repo
        self.embedding_client = embedding_client

    async def search(self, query: str):
        try:
            context = DataAgentContext(
                value_es_repo=self.value_es_repo,
                dw_mysql_repo=self.dw_mysql_repo,
                meta_mysql_repo=self.meta_mysql_repo,
                column_qdrant_repo=self.column_qdrant_repo,
                metric_qdrant_repo=self.metric_qdrant_repo,
                embedding_client=self.embedding_client
            )
            '''
            华北地区销售总额
            2025年各地区平均销售额
            各个地区iPhone去年卖了多少钱
            '''
            state = DataAgentState(query=query) # type: ignore

            async for chunk in graph.astream(
                input=state,
                context=context,
                stream_mode="custom"
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        
        except Exception as e:
            logger.exception(f"查询失败: {e}")
            yield f"data: {json.dumps({'error': e}, ensure_ascii=False, default=str)}\n\n"