from langchain.messages import HumanMessage

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime

from app.models.es.value_info_es import ValueInfoES
from app.prompt.load_prompt import load_prompt

async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("召回字段值")

    try:
        query = state["query"]
        keywords = state["keywords"]
        value_es_repo = runtime.context["value_es_repo"]

        # 调用大模型提取关键词
        prompt = load_prompt("extend_keywords_for_value_recall", query = query)
        messages = [HumanMessage(content=prompt)]
        chains = llm | JsonOutputParser()
        res = await chains.ainvoke(messages)

        # 将大模型提取的指标和jiaba分词后的词合并
        keywords = list(set(keywords + res))

        values_dict: dict[str, ValueInfoES] = {}
        for keyword in keywords:
            values = await value_es_repo.search(keyword) 

            for value in values:
                if value["id"] not in values_dict:
                    values_dict[value["id"]] = value

        recall_values: list[ValueInfoES] = list(values_dict.values())

        logger.info(f"召回字段值成功，召回的字段值为: {recall_values}")

        return {"recall_values": recall_values}

    except Exception as e:
        logger.exception(f"召回字段值失败: {e}")

