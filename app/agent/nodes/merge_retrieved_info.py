from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("合并召回")

    try:
        ...
    except Exception as e:
        logger.exception(f"合并召回失败: {e}")

    return state
