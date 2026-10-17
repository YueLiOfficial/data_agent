from langchain.messages import HumanMessage
import yaml

from app.agent.llm import llm
from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime

from app.prompt.load_prompt import load_prompt

async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("过滤表和字段")

    try:
        query = state["query"]
        table_infos = state["table_infos"]

        prompt = load_prompt("filter_table_info",
                    query=query, 
                    table_infos=yaml.dump(table_infos, allow_unicode=True, sort_keys=False)
                )
        messages = [HumanMessage(content=prompt)]
        chains = llm | JsonOutputParser()

        results = await chains.ainvoke(messages)

        # 将table_infos中没用的表和字段删除
        for table_info in table_infos[:]:
            if table_info["name"] not in results:
                table_infos.remove(table_info)
            else:
                for column in table_info["columns"][:]:
                    if column["name"] not in results[table_info["name"]]:
                        table_info["columns"].remove(column)

        logger.info(f"过滤表和字段完成，过滤后的值: {table_infos}")

        return {"table_infos": table_infos}
    except Exception as e:
        logger.exception(f"过滤表和字段失败: {e}")

