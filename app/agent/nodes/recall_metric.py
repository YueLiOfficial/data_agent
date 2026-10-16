from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    runtime.stream_writer("召回指标")

    try:
        ...
    except Exception as e:
        logger.exception(f"召回指标失败: {e}")

    return {
        
    } # type: ignore
