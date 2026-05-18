from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
import LearningTool
# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-5.4", api_key=api_key) 

reference_text = """
「脈象」是中醫「望、聞、問、切」四診中「切診」的核心，指手指感覺到的脈搏跳動形象。
透過感知脈搏的頻率、節律、強度、形態與流暢度，中醫師能了解氣血運行狀態、臟腑功能盛衰，進而診斷疾病、分析體質及預測預後。
以下為脈象的基礎知識簡介：
一、 把脈的位置：寸口脈中醫把脈主要位於手腕內側的「寸口」部位（橈動脈處），分為「寸、關、尺」三個區域：
關：位於手腕突起的橈骨莖突處。寸：關部前方（靠近手掌端），對應上半身與頭部。尺：關部後方（靠近手臂端），對應下半身與內臟（如肝、腎）。
二、 脈象的四大要素醫師在辨識脈象時，會從以下四個維度來體會：
位（深淺）：脈搏浮在表面（輕按即得）或沉在深處（重按才明顯）。
數（快慢）：脈搏跳動的次數與節律，正常人一息（呼吸一次）約跳 4~5 次。
形（形態）：脈管的粗細、軟硬與長短（如感覺像琴弦般緊繃或像水流般圓滑）。
勢（強弱）：脈搏的力量與流暢度（如充沛有力或微弱無力）。
"""

pulse_prompt = ChatPromptTemplate.from_messages([
    ('system', '請根據以下參考資料會回答使用者的問題，若資料不足請回答「資料不足，暫時無法回答」：\n\n{ref_text}'),
    ('human', '{question}')
])

prompt_value = pulse_prompt.invoke({"ref_text": reference_text, 
                                   "question": "請解釋脈象的基本特征。" })

response = llm.invoke(prompt_value)
print(response.content)

# Learning ToolMessage

