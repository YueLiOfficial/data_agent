import asyncio
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig) -> None:
        self.config = config
        self.client: Optional[AsyncElasticsearch] = None

    def init_client(self):
        self.client = AsyncElasticsearch(
            hosts=f"http://{self.config.host}:{self.config.port}"
        )

    async def close(self):
        if self.client:
            await self.client.close()
        self.client = None

es_client_manager = ESClientManager(app_config.es)

if __name__ == "__main__":
    async def test():
        es_client_manager.init_client()
        client = es_client_manager.client

        index_name = "books"

        assert client is not None
        if await client.indices.exists(index=index_name):
            await client.indices.delete(index=index_name)

        await client.indices.create(
            index=index_name,
        
            mappings={
                "dynamic": False,
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_data": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            },
        )

        await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
        )

        await client.indices.refresh(index=index_name)

        result = await client.search(
            index=index_name,
            query={
                "match": {
                    "name": "brave"
                }
            }
        )

        print(result)
        print("------------------------------------------")
        print(result["hits"]["hits"][0]["_source"])

        await es_client_manager.close()

    asyncio.run(test())

