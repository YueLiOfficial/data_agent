import asyncio

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.merge_retrieved_info import merge_retrieved_info
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.validate_sql import validate_sql
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.execute_sql import execute_sql

from langgraph.graph import END, StateGraph

from app.repositories.es.value_es_repository import ValueESRepoSitory
from app.repositories.qdrnt.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrnt.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.services.meta_knowledge_service import MetaKnowledgeService

from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.conf.meta_config import meta_config
from app.core.log import logger

from sqlalchemy.ext.asyncio import AsyncSession


builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

builder.add_node("extract_keywords",extract_keywords)
builder.add_node("recall_column",recall_column)
builder.add_node("recall_value",recall_value)
builder.add_node("recall_metric",recall_metric)
builder.add_node("merge_retrieved_info",merge_retrieved_info)
builder.add_node("filter_table",filter_table)
builder.add_node("filter_metric",filter_metric)
builder.add_node("add_extra_context",add_extra_context)
builder.add_node("generate_sql",generate_sql)
builder.add_node("validata_sql",validate_sql)
builder.add_node("correct_sql",correct_sql)
builder.add_node("execute_sql",execute_sql)

builder.set_entry_point("extract_keywords")
builder.add_edge("extract_keywords","recall_column")
builder.add_edge("extract_keywords","recall_value")
builder.add_edge("extract_keywords","recall_metric")
builder.add_edge("recall_column","merge_retrieved_info")
builder.add_edge("recall_value","merge_retrieved_info")
builder.add_edge("recall_metric","merge_retrieved_info")
builder.add_edge("merge_retrieved_info","filter_table")
builder.add_edge("merge_retrieved_info","filter_metric")
builder.add_edge("filter_table","add_extra_context")
builder.add_edge("filter_metric","add_extra_context")
builder.add_edge("add_extra_context","generate_sql")
builder.add_edge("generate_sql","validata_sql")
builder.add_conditional_edges(
    "validata_sql",
    lambda state: "correct_sql" if state.get("error") else "execute_sql",
    {
        "correct_sql": "correct_sql",
        "execute_sql": "execute_sql"
    }
)

builder.add_edge("correct_sql", "execute_sql")
builder.add_edge("execute_sql", END)

graph = builder.compile()

# print(graph.get_graph().draw_ascii())

if __name__ == "__main__":
    async def main():
        es_client_manager.init_client()
        dw_mysql_client_manager.init_client()
        meta_mysql_client_manager.init_client()
        qdrant_client_manager.init_client()
        embedding_client_manager.init_client()

        try:
            async with (
                dw_mysql_client_manager.session_fectory() as dw_session, # type: ignore
                meta_mysql_client_manager.session_fectory() as meta_session # type: ignore
            ):  
                dw_session: AsyncSession
                meta_session: AsyncSession

                context = DataAgentContext(
                    value_es_repo=ValueESRepoSitory(es_client_manager.client), # type: ignore
                    dw_mysql_repo=DWMysqlRepository(dw_session),
                    meta_mysql_repo=MetaMysqlRepository(meta_session),
                    column_qdrant_repo=ColumnQdrantRepository(qdrant_client_manager.client), # type: ignore
                    metric_qdrant_repo=MetricQdrantRepository(qdrant_client_manager.client), # type: ignore
                    embedding_client=embedding_client_manager.client, # type: ignore
                )


                '''
                华北地区销售总额
                2025年各地区平均销售额
                各个地区iPhone去年卖了多少钱
                '''
                state = DataAgentState(query="华北地区销售总额") # type: ignore

                async for chunk in graph.astream(
                    input=state,
                    context=context,
                    stream_mode="custom"
                ):
                    print(chunk)
                
                logger.success(f"查询成功")

        except Exception as e:
            logger.exception(f"查询失败: {e}")
        finally:
            await es_client_manager.close()
            await dw_mysql_client_manager.close()
            await meta_mysql_client_manager.close()
            await qdrant_client_manager.close()

    asyncio.run(main())