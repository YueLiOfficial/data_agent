from app.core.log import logger

from app.agent.state import ColumnInfoState, DataAgentState, MetricInfoState, TableInfoState
from app.agent.context import DataAgentContext


from langgraph.runtime import Runtime

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant

"""
1.收集一个最完整的字段信息列表 去重合并 dict[column_id,ColumnlnfoQdrant]
1.1.收集召回的字段信息列表
1.2.收集召回的指标信息列表联的字段信息列表
1.3.收集召回的字段值信息列表对应的字段信息列表=》将字段值保存到字段的值的样例列表中
1.4.收集相表的主键和外键字段信息列表
2.根据收集所有字段信息列表生成:带字段信息列表的表信息列表
2.1.对收集的字段信息列表进行按表id进行分组:dict[table_id, list[ColumnlnfoQdrant]]
2.2.生成带字段信息列表的表信息列表 -》table_infos:list[TablelnfoState]
    根据表id查询meta得到表信息
    根据当前字段信息列表·生成ColumnlnfoState类型的字段状态信息列表
2.3.整理recall_metrics
"""

async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "合并召回"})

    try:
        recall_columns = state["recall_columns"]
        recall_metrics = state["recall_metrics"]
        recall_values = state["recall_values"]
        meta_mysql_repo = runtime.context["meta_mysql_repo"]

        #1.收集一个最完整的字段信息列表 去重合并 dict[column_id,ColumnlnfoQdrant]
        column_info_dict: dict[str, ColumnInfoQdrant] = {}
        # 1.1.收集召回的字段信息列表
        for column in recall_columns:
            if column["id"] not in column_info_dict:
                column_info_dict[column["id"]] = column

        # 1.2.收集召回的指标信息列表关联的字段信息列表
        for metric in recall_metrics:
            for relevant_column in metric["relevant_columns"]:
                column_info: ColumnInfoMySQL = await meta_mysql_repo.get_column_info_by_id(relevant_column)
                column_id = column_info.id
                if column_id not in column_info_dict:
                    column = _convert_column_info_mysql_to_qdrant(column_info)
                    column_info_dict[column_id] = column

        # 1.3.收集召回的字段值信息列表对应的字段信息列表=》将字段值保存到字段的值的样例列表中
        for value in recall_values:
            column_id = value["column_id"]
            if column_id not in column_info_dict:
                column_info: ColumnInfoMySQL = await meta_mysql_repo.get_column_info_by_id(column_id)
                column_info_dict[column_id] = _convert_column_info_mysql_to_qdrant(column_info)
            # 将字段值添加到字段信息的examples中
            if value["value"] not in column_info_dict[column_id]:
                column_info_dict[column_id]["examples"].append(value["value"])

        # 2.根据收集所有字段信息列表生成:带字段信息列表的表信息列表
        table_column_info_dict: dict[str, list[ColumnInfoQdrant]] = {}
        # 2.1.对收集的字段信息列表进行按表id进行分组:dict[table_id, list[ColumnlnfoQdrant]]
        for column in column_info_dict.values():
            table_id = column["table_id"]
            if table_id not in table_column_info_dict:
                table_column_info_dict[table_id] = []
            table_column_info_dict[table_id].append(column)
            
        # 1.4.收集相关表的主键和外键字段信息列表
        for table_id, column_infos in table_column_info_dict.items():
            columns = await meta_mysql_repo.get_key_column_info_by_id(table_id)
            for column in columns:
                if column.id not in column_info_dict:
                    column_infos.append(_convert_column_info_mysql_to_qdrant(column))

        # 2.2.生成带字段信息列表的表信息列表 -》table_infos:list[TablelnfoState]
        #     根据表id查询meta得到表信息
        #     根据当前字段信息列表·生成ColumnlnfoState类型的字段状态信息列表
        table_infos: list[TableInfoState] = []
        for table_id, column_infos in table_column_info_dict.items():
            table_info: TableInfoMySQL = await meta_mysql_repo.get_table_info_by_table_id(table_id)
            table_infos.append(TableInfoState(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
                columns=_convert_column_infos_qdrant_to_state(column_infos)
            ))

        # 2.3 整理recall_metrics
        metric_infos: list[MetricInfoState] = _convert_metric_infos_qdrant_to_state(recall_metrics)

        logger.info(f"合并召回成功, 表信息列表：{table_infos}")
        logger.info(f"合并召回成功, 指标信息列表：{metric_infos}")

        return {"table_infos": table_infos, "metric_infos": metric_infos}
    except Exception as e:
        logger.exception(f"合并召回失败: {e}")

    return state


def _convert_column_info_mysql_to_qdrant(column_info: ColumnInfoMySQL) -> ColumnInfoQdrant:
    return ColumnInfoQdrant(
        id=column_info.id,
        name=column_info.name,
        type=column_info.type,
        role=column_info.role,
        examples=column_info.examples,
        description=column_info.description,
        alias=column_info.alias,
        table_id=column_info.table_id
    )

def _convert_column_infos_qdrant_to_state(column_infos: list[ColumnInfoQdrant]) -> list[ColumnInfoState]:
    return_list: list[ColumnInfoState] = []

    for column_info in column_infos:
        return_list.append(
            ColumnInfoState(
                name=column_info["name"],
                type=column_info["type"],
                role=column_info["role"],
                examples=column_info["examples"],
                description=column_info["description"],
                alias=column_info["alias"]
            )
        )

    return return_list

def _convert_metric_infos_qdrant_to_state(recall_metrics: list[MetricInfoQdrant]) -> list[MetricInfoState]:
    return_list: list[MetricInfoState] = []

    for metric in recall_metrics:
        return_list.append(
            MetricInfoState(
                name=metric["name"],
                description=metric["description"],
                relevant_columns=metric["relevant_columns"],
                alias=metric["alias"]
            )
        )    

    return return_list
