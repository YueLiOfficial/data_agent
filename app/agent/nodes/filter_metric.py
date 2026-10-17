from langchain.messages import HumanMessage
import yaml

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime

from app.prompt.load_prompt import load_prompt

async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "过滤指标"})

    try:
        query = state["query"]
        metric_infos = state["metric_infos"]

        prompt = load_prompt("filter_metric_info",
                    query=query, 
                    metric_infos=yaml.dump(metric_infos, allow_unicode=True, sort_keys=False)
                )
        messages = [HumanMessage(content=prompt)]
        chains = llm | JsonOutputParser()

        results = await chains.ainvoke(messages)

        # 将table_infos中没用的指标删除
        for metric_info in metric_infos[:]:
            if metric_info["name"] not in results:
                metric_infos.remove(metric_info)

        logger.info(f"过滤指标完成，过滤后的值: {metric_infos}")

        return {"metric_infos": metric_infos}
    except Exception as e:
        logger.exception(f"过滤指标失败: {e}")
