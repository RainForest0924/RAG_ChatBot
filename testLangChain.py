from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain.tools import tool
import LearningTool


# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4")

tools = [LearningTool.calculator, LearningTool.search_wikipedia]

agent = create_agent(
    model=llm, 
    tools=tools,
    system_prompt = """
    你是一個AI助手，專門用來回答使用者的問題。你可以使用以下工具來幫助你回答問題：
    1. 若需查詢資料，請使用LearningTool.search_wikipedia工具；
    2. 若需計算數學公式，請使用LearningTool.calculato；
    3. 若經過您的判斷不需要使用上述兩個工具即可回答，則可直接回答。
"""
    )

query = "台灣最高的山是哪一座，海拔多高？高度是幾公尺？台灣101的高度是幾公尺？台灣最高的山高度相當於幾座101？"

answer = agent.invoke(
    {
        "messages":[
            {
                "role":"user",
                "content":query
            }
        ]
    }
)

print("Answer:")
for i in range(len(answer["messages"])):
    print(answer["messages"][i].type)
    print(answer["messages"][i].content)