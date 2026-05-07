from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4", api_key=api_key)

messages = [SystemMessage(content="你是一個專業的醫學工程師，尤其擅長中醫脈診相關的知識。")]

messages.append(HumanMessage(content="請問中醫脈診的基本原理是什麼？"))

response = llm.invoke(messages)
print(response.content)

messages.append(AIMessage(content=response.content))

messages.append(HumanMessage(content="如果要開發一個脈診儀協助中醫師診斷脈象，推薦要用螺桿馬達還是氣囊式施壓？"))
response = llm.invoke(messages)
print(response.content)
# if isExist:
#     print("成功載入 .env 檔案")

# client = OpenAI()
# response = client.chat.completions.create(
#     model="gpt-5.4", messages=[
#         {"role": "user", "content": "你是誰？"},
#     ] )

# print(response.choices[0].message.content)

