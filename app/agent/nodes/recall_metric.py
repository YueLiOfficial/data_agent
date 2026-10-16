from langchain.messages import HumanMessage

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime

from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.prompt.load_prompt import load_prompt

async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("召回指标")

    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client = runtime.context["embedding_client"]
        metric_qdrant_repo = runtime.context["metric_qdrant_repo"]

        # 调用大模型提取关键词
        prompt = load_prompt("extend_keywords_for_metric_recall", query = query)
        messages = [HumanMessage(content=prompt)]
        chains = llm | JsonOutputParser()
        res = chains.invoke(messages)

        # 将大模型提取的指标和jiaba分词后的词合并
        keywords = list(set(keywords + res))

        # 将keywords向量化
        vectors = await embedding_client.aembed_documents(keywords)

        # 到qdrant库中查找对应的指标
        recall_metric_dict: dict[str, MetricInfoQdrant] = {}
        for vector in vectors:
            metric_infos = await metric_qdrant_repo.search(vector)

            # 将结果去重合并
            for metric in metric_infos:
                if metric["id"] not in recall_metric_dict:
                    recall_metric_dict[metric["id"]] = metric

        # 从字典中提取出结果
        recall_metrics: list[MetricInfoQdrant] = list(recall_metric_dict.values())

        logger.info(f"召回指标成功，召回的指标: {recall_metrics}")

        return {"recall_metrics": recall_metrics}

    except Exception as e:
        logger.exception(f"召回指标失败: {e}")
