from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4")

# Define Chain
rag_template = ChatPromptTemplate.from_messages([
    ("human", "請解釋一下什麼是{input}?")
])

general_template = ChatPromptTemplate.from_messages([
    ("human", "請回答一般的問題:{input}?")
])

rag_chain = rag_template | llm | StrOutputParser()
general_chain = general_template | llm | StrOutputParser()

def route_condition(input_text: str):
    if "RAG" in input_text or "rag" in input_text.upper():
        return "rag_chain"
    else:
        return "general_chain"

branch = RunnableBranch(
    (lambda x: route_condition(x["input"]) == "rag_chain", rag_chain),
    (lambda x: route_condition(x["input"]) == "general_chain", general_chain),
    general_chain  # Default to general_chain if no condition matches
)

# Test results
result = branch.invoke({"input": "RAG系統的用途是什麼，用100字內回答?"})
print(f"RAG Chain Result: {result}")