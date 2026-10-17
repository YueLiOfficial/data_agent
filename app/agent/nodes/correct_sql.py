from langchain.messages import HumanMessage
import yaml

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import StrOutputParser
from langgraph.runtime import Runtime

from app.prompt.load_prompt import load_prompt

async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("校正SQL")

    try:
        query = state["query"]
        metric_infos = state["metric_infos"]
        table_infos = state["table_infos"]
        date_info = state["date_info"]
        db_info = state["db_info"]
        sql = state["sql"]
        error = state["error"]
        
        prompt = load_prompt("correct_sql",
                    query=query, 
                    table_infos=yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
                    metric_infos=yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
                    date_info = yaml.dump(date_info, allow_unicode=True, sort_keys=False),
                    db_info = yaml.dump(db_info, allow_unicode=True, sort_keys=False),
                    sql = sql,
                    error = error
                )
        messages = [HumanMessage(content=prompt)]
        chains = llm | StrOutputParser()

        new_sql = await chains.ainvoke(messages)

        logger.info(f"校正SQL完成: {new_sql}")

        return {"sql": new_sql}
    except Exception as e:
        logger.exception(f"校正SQL失败: {e}")

    return state
