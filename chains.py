from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils import get_mongo_vectorstore, get_secret

from langchain_core.output_parsers import StrOutputParser

from RetrieveStrategy import parse_queries, query_prompt

def format_docs(docs):

    formatted_docs = []

    for doc in docs:

        question = doc.page_content
        answer = doc.metadata.get("answer", "")
        subject = doc.metadata.get("subject", "")
        symptom = doc.metadata.get("symptom", "")
        department = doc.metadata.get("department", "")
        gender = doc.metadata.get("gender", "")

        formatted_doc = f"""
                        患者性別:
                        {gender}    

                        患者主訴:
                        {question}

                        患者詢問主題:
                        {subject}

                        患者症狀概括:
                        {symptom}

                        參考科別:
                        {department}

                        參考建議:
                        {answer}

                        """

        formatted_docs.append(formatted_doc)

    return "\n\n".join(formatted_docs)
    

def retrieve_multiquery_documents(retriever, queries: List[str]):
    """使用多個查詢批次檢索，並保留完整 Document 物件及其 metadata。"""

    # 每個查詢都會對 MongoDB retriever 執行搜尋，最後合併所有搜尋結果。
    result_list = retriever.batch(queries)
    seen_content = set()
    unique_documents = []

    # 以 page_content 去重，避免同一份參考資料重複放入回答 context。
    for result in result_list:
        for doc in result:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                unique_documents.append(doc)

    return unique_documents


def get_suggestion_chain(question: str):
    prompt_template = PromptTemplate.from_template(
        """
        你是一位專業且從醫三十多年德高望重的醫生, 請根據下列症狀資訊, 匯整出一段簡短的醫學建議，回答過程需符合以下規范:
        1. 請使用繁體中文回答。
        2. 請以清楚、簡單易懂的方式回答，字數控制在300字以內。
        3. 請使用markdown格式回答，但不需要有標題。
        4. 請使用簡單的描述讓患者能夠理解，因為對象是患者，所以請不要出現任何專有名詞及英文縮寫或可能造成患者誤解的詞彙。
        5. 請針對患者的症狀進行詳細描述，並且提供可能的藥物或治療方案，診斷及建議。
        6. 請千萬避免洩露參考資料中患者及醫生提供的個人資訊。
        7. 請優先考慮參考資料中含有的症狀並給予建議。
        8. 若參考資料中找不到與患者提問相關資訊，請先告訴患者「我們沒有找到與您提問相關的醫療建議。」然後你可以自由發揮，依照患者的提問回答，但要注意禮貌。
        9. 如果患者的提問與醫療症狀無關，請先告訴患者「您的問題不涉及醫療建議，確定是要問這個問題嗎？」，得到肯定回答後你可以自由發揮，依照患者的提問回答，但要注意禮貌。

        參考資料:
        {context}

        患者提問:
        {question}
        """
    )

    with get_mongo_vectorstore() as vectorstore:
        llm = ChatOpenAI(model = "gpt-5.4", temperature = 0, max_tokens = 600, api_key=get_secret("OPENAI_API_KEY"))
        retriever = vectorstore.as_retriever(search_kwargs = {"k": 4})

        # 先將原始問題改寫成三個不同角度的查詢問題；main.py 仍只需傳入一個字串。
        query_generation_chain = query_prompt | llm | StrOutputParser()
        generated_query_text = query_generation_chain.invoke({"question": question})
        queries = parse_queries(generated_query_text)[:3]

        # 若模型輸出不足三個查詢，使用原始問題補足，確保批次檢索仍可執行。
        queries.extend([question] * (3 - len(queries)))

        # 使用三個查詢搜尋 MongoDB，合併並去除重複文件後建立回答 context。
        source_documents = retrieve_multiquery_documents(retriever, queries)
        context = format_docs(source_documents)

        # 回答仍以原始問題為主，三個查詢取得的資料則作為參考 context。
        result = (prompt_template | llm | StrOutputParser()).invoke(
            {
                "question": question,
                "context": context,
            }
        )

        # 維持 main.py 目前使用的回傳格式，讓 source_documents metadata 繼續可用。
        return {
            "result": result,
            "source_documents": source_documents,
        }

def debug_retriever(question: str):

    with get_mongo_vectorstore() as vectorstore:

        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )

        docs = retriever.invoke(question)

        print(f"找到 {len(docs)} 筆資料")

        for index, doc in enumerate(docs, start=1):

            print(
                f"\n========== Document {index} =========="
            )

            print("page_content:")
            print(doc.page_content)

            print("\nmetadata:")

            for key, value in doc.metadata.items():
                print(f"{key}: {value}")


# from pprint import pprint
# pprint(get_suggestion_chain("林醫師好:我是寒極生熱體質不知如何用食療法調整體質我吃到寒涼食物馬上手腳長滿尋痲疹吃到燥熱食物就頭頂長大痘和長痔瘡請求指點意見謝謝"))
