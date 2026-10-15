import asyncio
from typing import Optional
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.conf.app_config import DBConfig, app_config
from app.models.mysql.table_info_mysql import TableInfoMySQL



class MysqlClientManager:
    def __init__(self, config: DBConfig) -> None:
        self.config = config
        self.client: Optional[AsyncEngine] = None
        self.session_fectory: Optional[async_sessionmaker] = None

    def init_client(self):
        self.client = create_async_engine(
            url=f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}/{self.config.database}?charset=utf8mb4",
            pool_size=10,
            max_overflow=5
        )

        self.session_fectory = async_sessionmaker(
            bind=self.client,
            autoflush=False,
            autobegin=True # 自动开启事物
        )

    async def close(self):
        if self.client:
            await self.client.dispose()
            self.client = None

dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == "__main__":
    # async def test():
    #     dw_mysql_client.init_client()

    #     async with dw_mysql_client.session_fectory() as session:
    #         result = await session.execute(
    #             text("SELECT * FROM dim_product LIMIT 2")
    #         )

    #         # rows = result.all()
    #         # for row in rows:
    #         #     print(row.product_name)

    #         rows = result.mappings().all()
    #         for row in rows:
    #             print(row)
            
    #         # rows = result.scalars().all()
    #         # for val in rows:
    #         #     print(val)
        
    #     await dw_mysql_client.close()

    async def test_orm():
        meta_mysql_client_manager.init_client()

        assert meta_mysql_client_manager.session_fectory is not None
        async with meta_mysql_client_manager.session_fectory() as session:
            session: AsyncSession
            session.add(
                TableInfoMySQL(
                    id="1",
                    name="dim_customer1",
                    role="dim",
                    description="客户维度表1"
                )
            )

            session.add_all(
                [
                    TableInfoMySQL(
                        id="2",
                        name="dim_customer2",
                        role="dim",
                        description="客户维度表2"
                    ),
                    TableInfoMySQL(
                        id="3",
                        name="dim_customer3",
                        role="dim",
                        description="客户维度表3"
                    ),
                ]
            )
            # session.get(TableInfoMySQL, ident="id")
            await session.commit()

            result = await session.get(TableInfoMySQL, "1")

            assert result is not None
            print(result.name)
        await meta_mysql_client_manager.close()

    async def test_orm2():
        meta_mysql_client_manager.init_client()

        async with meta_mysql_client_manager.session_fectory() as session: # type: ignore
            session: AsyncSession
            table_info = await session.get(TableInfoMySQL, "1")

            table_info.name = "test" # type: ignore

            table_info2 = await session.get(TableInfoMySQL, "2")
            await session.delete(table_info2)

            await session.commit()

        await meta_mysql_client_manager.close()

    asyncio.run(test_orm2())
