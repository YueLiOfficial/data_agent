from app.core.log import logger

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

from langgraph.runtime import Runtime
from jieba.analyse import extract_tags

def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "提取关键字"})

    try:
        # 定义返回指定词性的元组
        allow_pos = (
            "n",  # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",  # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",  # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng",  # 英文
            "i",  # 成语
            "l",  # 常用固定短语
         )  

        query = state["query"]
        key_words:list[str] = extract_tags(query, topK=5, allowPOS=allow_pos) # type: ignore

        key_words.append(query)
        key_words = list(set(key_words))

        logger.info(f"提取关键词完成: {key_words}")
        state["keywords"] = key_words

        return state
    except Exception as e:
        logger.exception(f"提取关键字失败: {e}")
