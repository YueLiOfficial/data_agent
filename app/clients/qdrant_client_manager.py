import asyncio
import random

import qdrant_client
from qdrant_client import AsyncQdrantClient
from qdrant_client import models

from app.conf.app_config import app_config
from app.conf.app_config import QdrantConfig

from typing import Optional


class QdrantClientManager:
    def __init__(self, config: QdrantConfig) -> None:
        self.config = config
        self.client: Optional[AsyncQdrantClient] = None

    def init_client(self):
        self.client = qdrant_client.AsyncQdrantClient(
            f"{self.config.host}:{self.config.port}"
        )

qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == "__main__":
    async def main():
        qdrant_client_manager.init_client()
        client = qdrant_client_manager.client

        collection_name = "my_collection"

        # Create a collection
        assert client is not None
        if client.collection_exists(collection_name):
            await client.delete_collection(collection_name)

        await client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1024, 
                distance=models.Distance.COSINE
            ),
        )

        # Insert a vector
        await client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=i,  # 标识id
                    payload={
                        "color": "red" if i % 2 == 0 else "blue",
                    },
                    # 生成10维随机向量
                    vector=[random.random() for _ in range(1024)],
                )
                for i in range(10)  # 创建100个向量
            ],
        )

        # Search for nearest neighbors
        result = await client.query_points(
            collection_name=collection_name,
            query=[random.random() for _ in range(1024)],
            limit=2,
            score_threshold=0.1
        )

        for point in result.points:
            print(point.payload)

    asyncio.run(main())