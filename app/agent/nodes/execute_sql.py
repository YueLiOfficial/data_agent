from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("执行SQL")

    try:
        sql = state["sql"]
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        result = await dw_mysql_repo.execute_sql(sql)

        logger.info(f"执行SQL成功: {result}")

        runtime.stream_writer(result)

    except Exception as e:
        logger.exception(f"执行SQL失败: {e}")

    return state
