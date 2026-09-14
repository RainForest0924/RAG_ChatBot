import os
from dotenv import load_dotenv
from openai import embeddings
from pymongo import MongoClient
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
# from langchain_core.vectorstores import InMemoryVectorStore
# from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# from langchain_community.chat_message_histories import SQLChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory


# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

openai_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4", api_key=openai_key)

# Learning Mongo
embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

documents = [
    Document(page_content="LangChain是一個專門用於串接LLM與外部工具而設計的開源專案。",
             metadata={"source": "官方文件", "author" : "LangChain團隊", "date": "2024-06-01"}),
    Document(
        page_content="向量資料庫可以快速進行語義搜尋，提升RAG的精確度。",
             metadata={"source": "技術部落格", "author" : "技術達人", "date": "2025-05-25"}
    ),
    Document(
        page_content="透過metadata的篩選，更能有效提升資料檢索的精確度。",
             metadata={"source": "白皮書", "author" : "AI研究社", "date": "2025-07-19"}
    ),
]

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
collection = client["test"]["vectorstore"]

query = "什麼叫向量資料庫，在RAG裡面重要的用法又是什麼"
results = collection.aggregate([{
    "$vectorSearch":{
        "index": "vectorstore",
        "path": "embedding",
        "queryVector": embeddings.embed_query(query), 
        "numCandidates": 50, 
        "limit": 5
    }

}]
)

for result in results:
    print(result.get("text"))


# print(client.list_database_names())

# vector_store = MongoDBAtlasVectorSearch(
#     collection=client["test"]["vectorstore"],
#     embedding=embeddings,
#     index_name="vectorstore",
#     relevance_score_fn="cosine",
# )

# # vector_store.add_documents(documents)
# query = "什麼叫向量資料庫，在RAG裡面重要的用法又是什麼"
# search_result = vector_store.similarity_search(query, k = 1)

# for doc in search_result:
#     print(doc.page_content)
#     print(doc.metadata["date"])
