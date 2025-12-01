#pip install langchain-deepseek langchain-google-genai
import os
from dotenv import load_dotenv #load environment variables from .env file
import requests # scrape and load data from web pages
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI #for DeepSeek LLM
from langchain_google_genai import ChatGoogleGenerativeAI #for Google Gemini LLM

load_dotenv() #get environment variables

#Step 1: --------------------------- LLMS -------------------------------------
def get_deepseek():
    """
    returns a model object to invoke DeepSeek
    """
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    url = os.getenv("DEEPSEEK_API_BASE")

    llm_model = ChatOpenAI(
        model="deepseek-chat",
        max_tokens=1000,
        timeout=30,
        api_key=deepseek_key,
        base_url=url
    )
    return llm_model

def get_gemini():
    """
    returns a model to invoke Google Gimini.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    llm_model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=gemini_key,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    return llm_model

#Step 2: --------------------------- Tools -----------------------------------
@tool 
def get_news(topic: str) -> str:
    """get news updates information about a topic"""
    key = "pub_33ef6fb118884e11abaf69a3e3725060"
    url =  f"https://newsdata.io/api/1/latest?apikey=pub_33ef6fb118884e11abaf69a3e3725060&q={topic}"
    response = requests.get(url)
    return response.json()

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    response = requests.get(f'https://wttr.in/{location}?format=j1')
    return response.json()

@tool
def get_wisdom(topic: str) -> str:
    """Get wisdom for a topic"""
    match topic:
        case "life":
            return "its very short, be mindful"
        case "health":
            return "eat well and sleep well. Don't forget to exercise"
        case _:
            return "reflect more, learn more, act upon what you lear."

agent_tools=[get_news, get_weather, get_wisdom]
#Step 3: --------------------------- System Prompt ------------------------------
generic_prompt = """
You are a helpful chat assistant. You have tools that you can use if needed.
use get_weather tool when you need to fetch information about weather
use get_news tool when you need to fetch news updates about a topic
use get_wisdom tool when you want to advice or give a wisdom or recommendation
Understand the users intent and respond directly.
"""
#Step 4: -------------------------- User Question -------------------------------
# this is the main code to get a question and create an agent
user_question = input("Whats in your mind today?")
#Step 5: ---------------------------- Create Agent-------------------------------
#create an agent
agent = create_agent(
    model=get_deepseek(), #default Model
    middleware=[],
    tools=agent_tools,
    system_prompt=generic_prompt
    )
#Step 6: ------------------------ Call the Agent to Execute---------------------
#invoke the chatting agent
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": user_question}]
    }
)
#Step 7: ---------------------------- Access the Response Answer -------------
#print("Full Response:\n", result), #print("Messages:\n", result.get("messages"))
print("#"*30)
for i,message in enumerate(result.get("messages")):
    print(f"{i} : {message}\n--------------------\n")

print("#"*30)
print("Response:")
print(result["messages"][-1].content)
print("#"*30)