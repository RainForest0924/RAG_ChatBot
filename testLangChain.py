from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4")

# Learning Managing Conversation History
messages = []

messages.append(
    SystemMessage(content="你是一個中醫專家，尤其在脈象領域深耕數十年，造詣頗深。現在想向您請教脈診的問題")
)
messages.append(HumanMessage("什麼是滑脈，請用簡短三句話解釋?"))

response = llm.invoke(messages)

print(response.content)
messages.append(response)

messages.append(HumanMessage("滑脈的特徵是什麼?您剛才提到的那些體質又代表什麼樣的生理狀態，請依然用簡短的十句內語句解釋?"))

response = llm.invoke(messages)
print(response.content)
messages.append(response)
