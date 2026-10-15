

from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:
    def __init__(self, client: AsyncQdrantClient) -> None:
        self.client = client
        self.collection_name = "data-agent_column_collection2"

    async def _create_collection(self):
        if await self.client.collection_exists(self.collection_name):
            await self.client.delete_collection(self.collection_name)

        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=app_config.qdrant.embedding_size, 
                distance=models.Distance.COSINE
            ),
        )

    async def insert_column_infos(self, ids: list[str], payloads: list[ColumnInfoQdrant], vectors: list[list[float]]):
        await self._create_collection()
        
        batch_size = 16
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i: i + batch_size]
            batch_payloads = payloads[i: i + batch_size]
            batch_vectors = vectors[i: i + batch_size]

            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=id_,  # 标识id
                        payload=payload, # type: ignore
                        vector=vecotr,
                    )
                    for id_, payload, vecotr in zip(batch_ids, batch_payloads, batch_vectors)
                ],
            )