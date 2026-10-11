import utils
from functools import lru_cache
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from typing import List
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

openai_api_key = utils.get_secret("OPENAI_API_KEY")

documents = [
    "RAG系統的核心優勢在於它能夠結合預訓練模型的廣泛知識與即時、特定的外部數據，從而提供更準確更新更符合事實的答案。",
    "實現一個高效的RAG系統時，常見的挑戰包括如何設計最佳的Chunking策略以及優化檢索的精確度。",
    "與模型微調(fine-tuning)相比，RAG在知識更新上更具靈活性且成本較低，但對於學習特定風格或行為非其所長。",
    "提升RAG性能的關鍵步驟:資料前處理，選擇合適的Embedding模型，設計有效的檢索策略，以及後續的重排列(Re-ranking)。",
]

llm = ChatOpenAI(model="gpt-5.4", api_key=openai_api_key, temperature=0)


# 延後建立測試用向量資料庫，避免其他模組匯入本檔案時立即呼叫 embedding API。
@lru_cache(maxsize=1)
def get_demo_retriever():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_api_key)
    vectorstore = InMemoryVectorStore.from_texts(documents, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 3})

# Build multiquery retriever
query_prompt = ChatPromptTemplate.from_template(
        """
        你是一個實現多角度搜尋查詢的助手。

        請根據使用者原始問題，產生 3 個不同角度但語意相關的搜尋問題，
        用來提高向量資料庫檢索的召回率與精確度。

        每一行只輸出一個問題。
        不要編號。
        不要輸出其他說明。

        原始問題：
        {question}
        """
)

query_generation_chain = (
    query_prompt
    | llm
    | StrOutputParser()
)

def parse_queries(output: str) -> List[str]:
    return [line.strip() for line in output.strip().split('\n') if line.strip()]

def batch_retrieve_and_deduplicate(queries: List[str]) -> List[str]:
    # 這個 retriever 只供 RetrieveStrategy.py 的獨立測試使用。
    result_list = get_demo_retriever().batch(queries)
    seen_content = set()
    unique_results = []

    for result in result_list:
        for doc in result:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                unique_results.append(doc.page_content)

    return unique_results

multiquery_retriever_chain = (
    query_generation_chain 
    | RunnableLambda(parse_queries) 
    | RunnableLambda(batch_retrieve_and_deduplicate) 
)

if __name__ == "__main__":
    question = "RAG系統的優缺點是什麼?"
    retrieved_docs = multiquery_retriever_chain.invoke({"question": question})
    print(f"原始問題: {question}\n")
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"檢索結果 {i}: {doc}\n")

