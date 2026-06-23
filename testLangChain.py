from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_session_history(session_id: str) -> SQLChatMessageHistory:
    """
    Retrieve the chat message history for a given session ID.
    """
    return SQLChatMessageHistory(session_id=session_id,
                                 connection = "sqlite:///chat_history.db")

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4")

# Learning Managing Conversation History
chat_with_memory = RunnableWithMessageHistory(
    llm,
    get_session_history,
)

response = chat_with_memory.invoke(
    [
        SystemMessage(content="你是一個在脈象方面有專業知識且深耕數十載的中醫師。"),
        HumanMessage(content="請問脈象中，什麼是澀脈？用三句話簡短回答")
    ],
    config={"configurable": {
            "session_id": "Tony2"}
    }
)

print(response.content)

response = chat_with_memory.invoke(
    [
        HumanMessage(content="您剛才解釋的澀脈，有哪些典型的體質跟症狀？")
    ],
    config={"configurable": {
            "session_id": "Tony2"}
    }
)

print(response.content)

for msg in get_session_history("Tony2").messages:
    if isinstance(msg, SystemMessage):
        print(f"System: {msg.content}")
    elif isinstance(msg, HumanMessage):
        print(f"Human: {msg.content}")
    elif isinstance(msg, AIMessage):
        print(f"AI: {msg.content}")

