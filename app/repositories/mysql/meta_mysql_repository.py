from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.mysql.column_info_mysql import ColumnInfoMySQL

class MetaMysqlRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def save_table_infos(self, table_infos: list[TableInfoMySQL]):
        self.session.add_all(table_infos)

    def save_column_infos(self, column_infos: list[ColumnInfoMySQL]):
        self.session.add_all(column_infos)

    def save_metric_infos(self, metric_infos: list[MetricInfoMySQL]):
        self.session.add_all(metric_infos)

    def save_column_metric(self, column_metric: list[ColumnMetricMySQL]):
        self.session.add_all(column_metric)

    async def get_column_info_by_id(self, relevant_column) -> ColumnInfoMySQL:
        return await self.session.get(ColumnInfoMySQL, relevant_column) # type: ignore

    async def get_key_column_info_by_id(self, table_id: str) -> list[ColumnInfoMySQL]:
        result = await self.session.execute(
            select(ColumnInfoMySQL)
            .where(ColumnInfoMySQL.table_id == table_id)
            .where(ColumnInfoMySQL.role.in_(["foreign_key", "primary_key"]))
        )

        return list(result.scalars().all())

    async def get_table_info_by_table_id(self, table_id: str) -> TableInfoMySQL:
        return await self.session.get(TableInfoMySQL, table_id) # type: ignore