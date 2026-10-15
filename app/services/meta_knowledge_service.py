
from typing import Any
import uuid

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.conf.meta_config import MetaConfig, TableConfig, MetricConfig
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.repositories.es.value_es_repository import ValueESRepoSitory
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrnt.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrnt.metric_qdrant_repository import MetricQdrantRepository
from app.models.es.value_info_es import ValueInfoES
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.core.log import logger


class MetaKnowledgeService:
    def __init__(
        self,
        value_es_repo: ValueESRepoSitory,
        dw_mysql_repo: DWMysqlRepository,
        meta_mysql_repo: MetaMysqlRepository,
        column_qdrant_repo: ColumnQdrantRepository,
        metric_qdrant_repo: MetricQdrantRepository,
        embedding_client: HuggingFaceEndpointEmbeddings
    ):
        self.value_es_repo = value_es_repo
        self.dw_mysql_repo = dw_mysql_repo
        self.meta_mysql_repo = meta_mysql_repo
        self.column_qdrant_repo = column_qdrant_repo
        self.metric_qdrant_repo = metric_qdrant_repo
        self.embedding_client = embedding_client

    async def build(self, config: MetaConfig):
        """
        1. 将表信息、字段信息添加到meta库；
        2. 将字段信息添加到qdrant库；
        3. 将字段值添加到ES库；
        4. 将指标信息添加到meta库；
        5. 将指标信息添加到qdrant库。
        """

        # 1.将表信息、字段信息添加到meta库；
        column_infos = await self._save_table_column_info_to_meta(config.tables)
        logger.info(f"表信息、字段信息添加到meta库成功")

        # 2. 将字段信息添加到qdrant库；
        await self._save_column_infos_to_qdrant(column_infos)
        logger.info(f"字段信息添加到qdrant成功")

        # 3. 将字段值添加到ES库；
        await self._save_value_info_to_es(column_infos, config.tables)
        logger.info(f"字段值保存到ES库成功")

        # 4. 将指标信息添加到meta库；
        metric_infos = await self._save_metric_info_to_meta(config.metrics)
        logger.info(f"将指标信息添加到meta库成功")

        # 5. 将指标信息添加到qdrant库；
        await self._save_metric_infos_to_qdrant(metric_infos)
        logger.info(f"指标信息添加到qdrant成功")

    async def _save_table_column_info_to_meta(self, tables: list[TableConfig]) -> list[ColumnInfoMySQL]:
        table_infos: list[TableInfoMySQL] = []
        column_infos: list[ColumnInfoMySQL] = []

        for table in tables:
            table_infos.append(
                TableInfoMySQL(
                    id=table.name,
                    name=table.name,
                    role=table.role,
                    description=table.description
                )
            )

            column_type_dict: dict[str, str] = await self.dw_mysql_repo.get_column_type(table.name)
        
            for column in table.columns:
                values: list[Any] = await self.dw_mysql_repo.get_column_values(table.name, column.name)
                
                column_infos.append(
                    ColumnInfoMySQL(
                        id=f"{table.name}.{column.name}",
                        name=column.name,
                        type=column_type_dict.get(column.name),
                        role=column.role,
                        examples=values,
                        description=column.description,
                        alias=column.alias,
                        table_id=table.name
                    )
                )

        self.meta_mysql_repo.save_table_infos(table_infos)
        self.meta_mysql_repo.save_column_infos(column_infos)

        return column_infos


    async def _save_column_infos_to_qdrant(self, column_infos: list[ColumnInfoMySQL]):
        ids: list[str] = []
        payloads: list[ColumnInfoQdrant] = []
        vectors: list[list[float]] = []

        data_dict_list: list[dict] = []

        for column_info in column_infos:
            column_info_qdrant = ColumnInfoQdrant(
                id=column_info.id,
                name=column_info.name,
                type=column_info.type,
                role=column_info.role,
                examples=column_info.examples,
                description=column_info.description,
                alias=column_info.alias,
                table_id=column_info.table_id
            )

            # 保存字段的name
            data_dict_list.append({
                "id": uuid.uuid4(),
                "payload": column_info_qdrant,
                "text": column_info.name
            })
            # 保存字段的description
            data_dict_list.append({
                "id": uuid.uuid4(),
                "payload": column_info_qdrant,
                "text": column_info.description
            })
            # 保存字段的alias
            for alia in column_info.alias:
                data_dict_list.append({
                    "id": uuid.uuid4(),
                    "payload": column_info_qdrant,
                    "text": alia
                })

        texts = []
        for data in data_dict_list:
            ids.append(data["id"])
            payloads.append(data["payload"])
            texts.append(data["text"])
        
        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i: i + batch_size]
            batch_vectors = await self.embedding_client.aembed_documents(batch_texts)
            vectors.extend(batch_vectors)

        await self.column_qdrant_repo.insert_column_infos(ids, payloads, vectors)
            

    async def _save_value_info_to_es(self, column_infos: list[ColumnInfoMySQL], tables: list[TableConfig]):
        values_infos: list[ValueInfoES] = []

        column_sync_dict = {}

        # 记录每一列是否需要检索
        for table in tables:
            for column in table.columns:
                column_sync_dict[f"{table.name}.{column.name}"] = column.sync

        for column_info in column_infos:
            sync = column_sync_dict[column_info.id]
            if sync:
                values = await self.dw_mysql_repo.get_column_values(column_info.table_id, column_info.name, 100000)

                for value in values:
                    values_infos.append(
                        ValueInfoES(
                            id=f"{column_info.id}.{value}",
                            value=value,
                            type=column_info.type,
                            column_id=column_info.id,
                            column_name=column_info.name,
                            table_id=column_info.table_id,
                            table_name=column_info.table_id
                        )
                    )

        await self.value_es_repo.insert_values(values_infos)


    async def _save_metric_info_to_meta(self, metrics: list[MetricConfig]) -> list[MetricInfoMySQL]:
        metric_infos = []
        metric_column = []
        
        for metric in metrics:
            metric_infos.append(
                MetricInfoMySQL(
                    id=metric.name,
                    name=metric.name,
                    description=metric.description,
                    relevant_columns=metric.relevant_columns,
                    alias=metric.alias
                )
            )

            for relevant_column in metric.relevant_columns:
                metric_column.append(
                    ColumnMetricMySQL(
                        column_id=relevant_column,
                        metric_id=metric.name
                    )
                )

        self.meta_mysql_repo.save_metric_infos(metric_infos)
        self.meta_mysql_repo.save_column_metric(metric_column)

        return metric_infos

    async def _save_metric_infos_to_qdrant(self, metric_infos: list[MetricInfoMySQL]):
        ids: list[str] = []
        payloads: list[MetricInfoQdrant] = []
        vectors: list[list[float]] = []

        data_dict_list: list[dict] = []

        for metric_info in metric_infos:
            metric_info_qdrant = MetricInfoQdrant(
                id=metric_info.id,
                name=metric_info.name,
                description=metric_info.description,
                alias=metric_info.alias,
                relevant_columns=metric_info.relevant_columns
            )

            # 保存字段的name
            data_dict_list.append({
                "id": uuid.uuid4(),
                "payload": metric_info_qdrant,
                "text": metric_info.name
            })
            # 保存字段的description
            data_dict_list.append({
                "id": uuid.uuid4(),
                "payload": metric_info_qdrant,
                "text": metric_info.description
            })
            # 保存字段的alias
            for alia in metric_info.alias:
                data_dict_list.append({
                    "id": uuid.uuid4(),
                    "payload": metric_info_qdrant,
                    "text": alia
                })

        texts = []
        for data in data_dict_list:
            ids.append(data["id"])
            payloads.append(data["payload"])
            texts.append(data["text"])
        
        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i: i + batch_size]
            batch_vectors = await self.embedding_client.aembed_documents(batch_texts)
            vectors.extend(batch_vectors)

        await self.metric_qdrant_repo.insert_metric_infos(ids, payloads, vectors)
            