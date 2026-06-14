from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Get the OpenAI API key from environment variables
# api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4")
embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

# Practice Retrieval Augmented Generation (RAG)
texts = [
     "滑脈的脈波波形較圓滑，頻譜能量通常集中於低頻區域。",
    "弦脈具有較陡峭的上升緣，因此中頻成分可能較為明顯。",
    "澀脈波形不規則且不流暢，高頻能量分布可能較分散。",
    "SER(10)定義為0至10Hz頻譜能量與10至50Hz頻譜能量之比值。",
    "5至10Hz頻段在滑弦澀分類中具有較高的判別能力。",
    "脈波頻譜可利用快速傅立葉轉換FFT進行分析。",
    "頻譜熵Spectral Entropy可量化頻譜能量分布的離散程度。",
    "LF頻段定義為0.04至0.15Hz。",
    "HF頻段定義為0.15至0.40Hz。",
    "LFHF比值常被用來評估交感與副交感神經活性。",
    "SDNN反映整體心率變異程度。",
    "RMSSD主要反映副交感神經活動。",
    "多項羅吉斯迴歸MNLogit可用於滑弦澀三分類模型建立。",
    "脈波振幅空間分布可利用24通道感測器進行量測。",
    "熱圖Heatmap能夠直觀呈現脈波振幅在感測器陣列上的分布。"
]

vectorstore = InMemoryVectorStore.from_texts(texts, embeddings)
retriever = vectorstore.as_retriever()

prompt = ChatPromptTemplate.from_template("""
你是一位中醫師，尤其對脈診有深入研究，有幾十年的經驗。
請根據以下提供的參考資料回答問題，並給出參考的段落。
請保持簡潔的回復，不超過三句話。
如果提供的資料沒有可以回答問題的，就請說「根據提供的資料，無法回答此問題」。
參考資料:{context}
問題:{question}
回答：                                         
"""
)

rag_chain = (
    {
        "context": retriever|format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

query = "滑脈的頻譜能量通常集中在哪個頻段，該頻段的意義是什麼？"

answer = rag_chain.invoke(query)

print("Answer:")
print(answer)

docs = retriever.invoke(query)
for doc in docs:
    print("-",doc.page_content)
