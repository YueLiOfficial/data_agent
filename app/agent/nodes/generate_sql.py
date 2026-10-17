from langchain.messages import HumanMessage
import yaml

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import StrOutputParser
from langgraph.runtime import Runtime

from app.prompt.load_prompt import load_prompt

async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("生成SQL")

    try:
        query = state["query"]
        metric_infos = state["metric_infos"]
        table_infos = state["table_infos"]
        date_info = state["date_info"]
        db_info = state["db_info"]
        
        prompt = load_prompt("generate_sql",
                    query=query, 
                    table_infos=yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
                    metric_infos=yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
                    date_info = yaml.dump(date_info, allow_unicode=True, sort_keys=False),
                    db_info = yaml.dump(db_info, allow_unicode=True, sort_keys=False)
                )
        messages = [HumanMessage(content=prompt)]
        chains = llm | StrOutputParser()

        sql = await chains.ainvoke(messages)

        logger.info(f"生成SQL完成: {sql}")

        return {"sql": sql}
    except Exception as e:
        logger.exception(f"生成SQL失败: {e}")
