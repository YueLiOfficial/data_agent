from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("添加额外信息")

    try:
        ...
    except Exception as e:
        logger.exception(f"添加额外信息失败: {e}")

    return state
