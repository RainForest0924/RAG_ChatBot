from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from utils import get_mongo_vectorstore

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):

    formatted_docs = []

    for doc in docs:

        question = doc.page_content
        answer = doc.metadata.get("answer", "")
        subject = doc.metadata.get("subject", "")
        symptom = doc.metadata.get("symptom", "")
        department = doc.metadata.get("department", "")

        formatted_doc = f"""
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
    

def get_suggestion_chain(question:str):
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

    llm = ChatOpenAI(model = "gpt-5.4", temperature = 0, max_tokens = 600)

    with get_mongo_vectorstore() as vectorstore:
        retriever = vectorstore.as_retriever(search_kwargs = {"k": 4})
        retrieve_chain = {
            "question": RunnablePassthrough(),
            "source_documents": retriever
                        }
        
        rag_chain = (
                    retrieve_chain | 
                    RunnablePassthrough.assign(
                    context=lambda x: format_docs(x["source_documents"])
                    )
                    | RunnablePassthrough.assign(
                                        result=(
                                        RunnableLambda(
                                            lambda x: {
                                                "question": x["question"],
                                                "context": x["context"]
                                                }
                                                        )
                    | prompt_template | llm | StrOutputParser()
                                                )
                                                )
                    )

        result = rag_chain.invoke(question)

        return result

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


from pprint import pprint
pprint(get_suggestion_chain("林醫師好:我是寒極生熱體質不知如何用食療法調整體質我吃到寒涼食物馬上手腳長滿尋痲疹吃到燥熱食物就頭頂長大痘和長痔瘡請求指點意見謝謝"))