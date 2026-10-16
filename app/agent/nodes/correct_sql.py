from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("校正SQL")

    try:
        ...
    except Exception as e:
        logger.exception(f"校正SQL失败: {e}")

    return state
