from app.core.log import logger
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer("校验SQL")

    try:
        sql = state["sql"]
        dw_mysql_repo = runtime.context["dw_mysql_repo"]
        
        await dw_mysql_repo.validate_sql(sql)

        logger.info(f"校验SQL成功")

        return {"error": None}
    except Exception as e:
        logger.exception(f"校验SQL失败: {e}")

        return {"error": f"校验SQL失败: {e}"}

