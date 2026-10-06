import utils
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_core.vectorstores import InMemoryVectorStore
# from typing import List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.stores import InMemoryStore
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.retrievers import ParentDocumentRetriever

# documents = [
#     "RAG系統的核心優勢在於它能夠結合預訓練模型的廣泛知識與即時、特定的外部數據，從而提供更準確更新更符合事實的答案。",
#     "實現一個高效的RAG系統時，常見的挑戰包括如何設計最佳的Chunking策略以及優化檢索的精確度。",
#     "與模型微調(fine-tuning)相比，RAG在知識更新上更具靈活性且成本較低，但對於學習特定風格或行為非其所長。",
#     "提升RAG性能的關鍵步驟:資料前處理，選擇合適的Embedding模型，設計有效的檢索策略，以及後續的重排列(Re-ranking)。",
# ]

# llm = ChatOpenAI(model="gpt-5.4", api_key=openai_api_key, temperature=0)
# embeddings = OpenAIEmbeddings(model = "text-embedding-3-small", api_key=openai_api_key)
# vectorestore = InMemoryVectorStore.from_texts(documents, embeddings)
# retriever = vectorestore.as_retriever(search_kwargs={"k": 3})

# Build multiquery retriever
# query_prompt = ChatPromptTemplate.from_template(
#         """
#         你是一個實現多角度搜尋查詢的助手。

#         請根據使用者原始問題，產生 3 個不同角度但語意相關的搜尋問題，
#         用來提高向量資料庫檢索的召回率與精確度。

#         每一行只輸出一個問題。
#         不要編號。
#         不要輸出其他說明。

#         原始問題：
#         {question}
#         """
# )

# query_generation_chain = (
#     query_prompt
#     | llm
#     | StrOutputParser()
# )

# def parse_queries(output: str) -> List[str]:
#     return [line.strip() for line in output.strip().split('\n') if line.strip()]

# def batch_retrieve_and_deduplicate(queries: List[str]) -> List[str]:
#     result_list = retriever.batch(queries)
#     seen_content = set()
#     unique_results = []

#     for result in result_list:
#         for doc in result:
#             if doc.page_content not in seen_content:
#                 seen_content.add(doc.page_content)
#                 unique_results.append(doc.page_content)

#     return unique_results

# multiquery_retriever_chain = (
#     query_generation_chain 
#     | RunnableLambda(parse_queries) 
#     | RunnableLambda(batch_retrieve_and_deduplicate) 
# )

openai_api_key = utils.get_secret("OPENAI_API_KEY")

docs = [
    {
        "doc_id": "LAW-001",
        "content": "勞動基准法第38條:勞工在同一雇主或事業單位，繼續工作滿一定期間者，應依下列規定給予特別休假： \
            一、六個月以上一年未滿者，三日。二、一年以上二年未滿者，七日。\
            三、二年以上三年未滿者，十日。四、三年以上五年未滿者，每年十四日。 \
            五、五年以上十年未滿者，每年十五日。六、十年以上者，每一年加給一日，加至三十日為止。\
            前項之特別休假期日，由勞工排定之。"
    }
]

child_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=15)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)

parent_retriever = ParentDocumentRetriever(
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
    vectorstore = InMemoryVectorStore(embedding=OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_api_key)),
    docstore = InMemoryStore(),
)

documents = [
    Document(page_content = d["content"], metadata = {"doc_id": d["doc_id"]}) for d in docs
]
parent_retriever.add_documents(documents)

query = "勞工工作半年特休幾天?"
retrieve_docs = parent_retriever.invoke(query)
print(f"\n --- 檢索到的父文件共 {len(retrieve_docs)} 個 --- \n")
print(retrieve_docs[0].page_content)

"""
"""
# question = "RAG系統的優缺點是什麼?"
# retrieved_docs = multiquery_retriever_chain.invoke({"question": question})
# print(f"原始問題: {question}\n")
# for i, doc in enumerate(retrieved_docs, 1):
#     print(f"檢索結果 {i}: {doc}\n")



