from datetime import datetime

from app.core.log import logger

from app.agent.state import DBInfoState, DataAgentState, DateInfoState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "添加额外信息"})

    try:
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        today = datetime.today()
        date = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month+2)//3}"  # Q1-Q4

        date_info = DateInfoState(
            date=date,
            weekday=weekday,
            quarter=quarter
        )

        mysql_info = await dw_mysql_repo.get_db_info()
        db_info = DBInfoState(
            version=mysql_info["version"],
            dialect=mysql_info["dialect"]
        )

        logger.info(f"添加额外信息完成, date_info: {date_info}, db_info: {db_info}")

        return {
            "date_info": date_info,
            "db_info": db_info
        }

    except Exception as e:
        logger.exception(f"添加额外信息失败: {e}")
