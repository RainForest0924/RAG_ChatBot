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
llm_with_tools = llm.bind_tools([LearningTool.get_current_weather])
messages = [
    SystemMessage(content="你是一個能及時查詢天氣的助理"),
    HumanMessage(content="請問現在台灣新竹市的天氣如何？")
]

response = llm_with_tools.invoke(messages)
pprint(response.tool_calls)

if response.tool_calls:
    tool_response = response.tool_calls[0]
    weather_result = LearningTool.get_current_weather.invoke(input = tool_response.get('args'))

    messages.append(AIMessage(content="", tool_calls=[tool_response]))
    messages.append(ToolMessage(content= weather_result, tool_call_id = tool_response["id"]))
    messages.append(HumanMessage(content="請問現在新竹市的天氣如何，需要帶傘嗎?"))

    response_final = llm_with_tools.invoke(messages)
    print(response_final.content)

else:
    print(f"LLM 回應: {response.content}")



# Learning ToolMessage

