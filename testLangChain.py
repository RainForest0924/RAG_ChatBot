from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents  import Document
import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

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

vector_store = InMemoryVectorStore.from_documents(documents, embeddings)

query = "什麼是LangChain?"
filter_criteria = {"author": "LangChain團隊"}
filter_responses = vector_store.similarity_search(query, k=1, filter= lambda doc: doc.metadata.get("author") == filter_criteria["author"])

for doc in filter_responses:
    print(f"Content: {doc.page_content}")
    print(f"Source: {doc.metadata['source']}")
    print(f"Author: {doc.metadata['author']}")
    print(f"Date: {doc.metadata['date']}")
