from typing import TypedDict
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.repositories.es.value_es_repository import ValueESRepoSitory
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrnt.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrnt.metric_qdrant_repository import MetricQdrantRepository

# 包含一些固定的数据或依赖的模块
class DataAgentContext(TypedDict):
    embedding_client: HuggingFaceEndpointEmbeddings # 向量服务器客户端
    column_qdrant_repo: ColumnQdrantRepository # 字段向量库
    metric_qdrant_repo: MetricQdrantRepository # 指标向量库
    value_es_repo: ValueESRepoSitory # 字段值全文索引库
    meta_mysql_repo: MetaMysqlRepository # 元数据库
    dw_mysql_repo: DWMysqlRepository # 数据仓库
