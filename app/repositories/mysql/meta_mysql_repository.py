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