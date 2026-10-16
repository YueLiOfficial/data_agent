from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("召回字段")

    try:
        ...
    except Exception as e:
        logger.exception(f"召回字段失败: {e}")

    return {
        
    } # type: ignore
