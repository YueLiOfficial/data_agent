from langchain.messages import HumanMessage

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime

from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.prompt.load_prompt import load_prompt

async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("召回字段")

    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client = runtime.context["embedding_client"]
        column_qdrant_repo = runtime.context["column_qdrant_repo"]

        # 调用大模型提取关键词
        prompt = load_prompt("extend_keywords_for_column_recall", query = query)
        messages = [HumanMessage(content=prompt)]
        chains = llm | JsonOutputParser()
        res = await chains.ainvoke(messages)

        # 将大模型提取的关键词和jiaba分词后的词合并
        keywords = list(set(keywords + res))

        # 将关键词向量化
        vectors = await embedding_client.aembed_documents(keywords)

        # 到qdrant库中查找对应的字段
        recall_column_dict: dict[str, ColumnInfoQdrant] = {}
        for vector in vectors:
            column_infos = await column_qdrant_repo.search(vector)

            # 将结果去重合并
            for column in column_infos:
                if column["id"] not in recall_column_dict:
                    recall_column_dict[column["id"]] = column

        # 从字典中提取出结果
        recall_columns: list[ColumnInfoQdrant] = list(recall_column_dict.values())

        logger.info(f"召回字段成功，召回的字段: {recall_columns}")

        return {"recall_columns": recall_columns}

    except Exception as e:
        logger.exception(f"召回字段失败: {e}")
