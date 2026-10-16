from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("生成SQL")

    try:
        ...
    except Exception as e:
        logger.exception(f"生成SQL失败: {e}")

    return state
