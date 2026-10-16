from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

load_dotenv(override=True)

llm = init_chat_model(
    model="qwen3.7-flash",
    model_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    extra_body={
        "enable_thinking": False
    }
)

if __name__ == "__main__":
    messages = [
        HumanMessage(content="你好")
    ]

    chains = llm | StrOutputParser()

    res = chains.invoke(messages)

    print(res)