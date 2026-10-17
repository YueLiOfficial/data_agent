import asyncio
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import dw_mysql_client_manager
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.mysql.column_info_mysql import ColumnInfoMySQL

class DWMysqlRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_column_type(self, table: str) -> dict[str, str]:
        column_type_dict: dict[str, str] = {}

        sql = f"SHOW COLUMNS FROM {table}"

        result = await self.session.execute(text(sql))

        column_type_dict = {item.Field:item.Type for item in result.all()}

        return column_type_dict

    async def get_column_values(self, table, column, limit = 10) -> list[Any]:
        sql = f"SELECT DISTINCT {column} FROM {table} LIMIT {limit}"

        result = await self.session.execute(text(sql))

        values = result.scalars().all()

        return list(values)

    async def get_db_info(self) -> dict:
        version = await self.session.execute(
            text("SELECT @@version")
        )

        version = version.scalar()
        dialect = self.session.bind.dialect.name

        return {"version": version, "dialect": dialect}

        

if __name__ == "__main__":
    
    async def test():
        dw_mysql_client_manager.init_client()
        async with dw_mysql_client_manager.session_fectory() as session: # type: ignore
            dw = DWMysqlRepository(session=session)

            await dw.get_column_values("dim_customer", "gender")

    asyncio.run(test())