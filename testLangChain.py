from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents  import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4")

# Generate Keywords
keywords_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一個關鍵詞的生成助手"),
    ("user", "請產生一個適合用於搜尋的關鍵字，關於：{input}")
])
keyword_chain = keywords_prompt | llm

# Search based on keywords
search_prompt = ChatPromptTemplate.from_messages([
    ("system", "妳是一個搜尋與資料統整助手。"),
    ("user", "請根據以下關鍵字搜尋相關的資訊：{keywords}")
])
search_chain = search_prompt | llm

# Combine
chain = (
    {"keywords": keyword_chain, "input": RunnablePassthrough()} |
    RunnableLambda(lambda x: {
        "keywords": x["keywords"].content 
    }) |
    search_prompt | 
    llm
)

input_text = "RAG在醫療領域如何應用"
results = chain.invoke(input_text)

print("關鍵字： ",  keyword_chain.invoke({"input": input_text}).content)
print("搜尋結果： ", results.content)