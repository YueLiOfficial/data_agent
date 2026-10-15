from elasticsearch import AsyncElasticsearch

from app.models.es.value_info_es import ValueInfoES

class ValueESRepoSitory:
    def __init__(self, client: AsyncElasticsearch) -> None:
        self.client = client
        self.index_name = "data-agent-value_index2"

    async def _create_index(self):
        if await self.client.indices.exists(index=self.index_name):
            await self.client.indices.delete(index=self.index_name)

        await self.client.indices.create(
            index=self.index_name,
            mappings={
                "dynamic": False,
                "properties": {
                    "id": {"type": "keyword", "index":False},
                    "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word", "index": True},
                    "type": {"type": "keyword", "index":False},
                    "column_id": {"type": "keyword", "index":False},
                    "column_name": {"type": "keyword", "index":False},
                    "table_id": {"type": "keyword", "index":False},
                    "table_name": {"type": "keyword", "index":False},
                }
            }
        )

    async def insert_values(self, value_infos: list[ValueInfoES]):
        await self._create_index()

        batch_size = 30

        for i in range(0, len(value_infos), batch_size):
            batch_value_infos = value_infos[i: i + batch_size]
            
            operations: list[dict] = []
            
            for value in batch_value_infos:
                
                operations.append({
                    "index": {
                        "_index": self.index_name
                    }
                })

                operations.append(value) # type: ignore

            await self.client.bulk(
                operations=operations
            )