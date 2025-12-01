from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv() #get environment variables

#----------------- Sample Fixed Database ----------------------------
ACCOUNTS = {
    "cash": 100,
    "account receivable": 20100,
    "payroll": 1000000
}

CUSTOMERS_DEBT = {
    "Ali" : { "debt": 1300, "days_overdue": 30 },
    "Malik": { "debt": 700, "days_overdue": 90 },
    "Fatima": { "debt": 500, "days_overdue": 45 }
}

INVENTORY = {
    "laptops": {"minimum_quantity": 10, "current_quantity": 5, "supplier": "Qataranji"},
    "keyboards": {"minimum_quantity": 30, "current_quantity": 45, "supplier": "Teck World"},
    "monitors": {"minimum_quantity": 20, "current_quantity": 15, "supplier": "Tahhan+"},
}

#Step 1: ----------------- LLMS Declaration ----------------------------
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

# Shared LLM
llm = get_deepseek()

# Step 2: -------------------- State Definition ---------------------
class AgentState(TypedDict):
    query: str
    classification: str | None
    account_balance: int | None
    llm_assessment: str | None
    message: str | None
    inventory_quantity: dict | None
    final_answer: str | None

# Step 3: --------------------- Create Graph Nodes --------------------
# Node 1: @@@@@ Classify the User Query @@@@@
def classify_question(state: AgentState):
    prompt = f"""
    Classify this question strictly as either:
    - 'accounting'
    - 'inventory'
    Question: {state['query']}
    Answer with ONLY the label.
    """
    label = llm.invoke(prompt).content.strip().lower()
    return {"classification": label}

@tool
def get_account_balance(query: str) -> str:
    """get account balance from user query"""

    for name in ACCOUNTS:
        if name in query:
            balance = ACCOUNTS[name]
            result = f"Account Name: {name}, Balance: {balance}"
            print(result) ################Debug
            return result

    return None

# Node 2: @@@@@ Accounting - Lookup Account Balance @@@@@
def accounting_lookup(state: AgentState):
    query = state["query"].lower()

    prompt = f"""
        You are an assistant agent that can find account name and balance using tool function call based on user input query.
        The account name is mentioned in the query. We need to pass the query to the tool to extract the name and balance
        based on the account name mentioned in the query.
        """
    agent = create_agent(
        model = llm, 
        tools=[get_account_balance],
        system_prompt=prompt
        )
    result = agent.invoke(
        {
            "messages": query
        }
    )
    balance = result["messages"][-1].content
    return {"account_balance": balance}

# Node 3: @@@@@ Accounting - LLM Assessment Node @@@@@
def accounting_assessment(state: AgentState):
    balance = state["account_balance"]
    prompt = f"""
    The name and balance of a business account is: {balance}. 
    classify this accoung balance according to your best judgement 
    for a small business shop strictly as either:
    - 'low'
    - 'acceptable'
    Answer with ONLY the label
    """
    text = llm.invoke(prompt).content.strip().lower()
    print("LLM account assessment: ", text) #################Debug
    return {"llm_assessment": text}

@tool
def get_overdue_customer_debt() -> str:
    """Get the most overdue customer debt"""
    customer_name = ""
    max_overdue = 0
    debt = 0
    for name, data in CUSTOMERS_DEBT.items():
        if data["days_overdue"] > max_overdue:
            max_overdue = data["days_overdue"]
            customer_name = name
            debt = data["debt"]

    result = f"Customer: {customer_name} has debt amount: {debt} overdue for {max_overdue} days."
    print("Customer overdue Info: ", result) #################Debug
    return result

#Node 4: @@@@@ Accounting - Collect Debt from customer with highest overdue @@@@@
def collect_debt(state: AgentState):
    llm_assessment = state["llm_assessment"]

    if llm_assessment is None:
        return {"customer_message": "No suggestion"}
    elif llm_assessment.lower().strip() == 'low':
        prompt = f"""
        You are an assistant agent that can find the most overdue customer debt using tool function call.
        The information returned from the tool includes the Customer name, debt amount and overdue in days.
        Use the information provided by the tool to draft a nice message text reminder that we can use 
        to send it as an email to remind the customer to pay ASAP.
        """
        agent = create_agent(
            model = llm, 
            tools=[get_overdue_customer_debt],
            system_prompt=prompt
            )
        result = agent.invoke(
            {
                "messages": "get customer with longest debt overdue and prepare message to send notification"
            }
        )
        text = result["messages"][-1].content
        message = "**Recommendation to collect debt. Here is prepared draft to send to customer:**\n\n"
        return {"message": message + text}
    else:
        return {"message": "No further action needed."}
    
# Node 5: @@@@@ Accounting - Good standing Account @@@@@
def accounting_assessment_good(state: AgentState):
    balance = state["account_balance"]
    prompt = f"""
    Provide a concise and a very short assessment of two or three sentences ONLY about the following 
    account balance for a small retail business. The account name and balance is: {balance}. 
    Do you think the balance of this specific account is adequate for this specific account? 
    Answer very briefly.
    """
    text = llm.invoke(prompt).content
    return {"message": text}

# Node 6: %%%% Inventory Lookup Node %%%%
def inventory_lookup(state: AgentState):
    query = state["query"].lower()

    found_item = None
    for item in INVENTORY:
        if item in query:
            found_item = item
            break

    if found_item is None:
        return {"inventory_quantity": None}

    qty_data = INVENTORY[found_item]
    return {"inventory_quantity": qty_data}

# Node 7: %%%% Inventory - LLM Assessment Node %%%%
def inventory_assessment(state: AgentState):
    qty_info = state["inventory_quantity"]

    if qty_info is None:
        return {"llm_assessment": "Item not found."}

    prompt = f"""
    Current qty: {qty_info['current_quantity']}
    Minimum qty: {qty_info['minimum_quantity']}
    Provide advice on whether to restock and by how much. 
    Be brief and answer in three to four sentences ONLY.
    """
    text = llm.invoke(prompt).content
    return {"message": text}

# Node 8: &&&& Final Formatting Node &&&&
def format_response(state: AgentState):
    formatted = f"""
    QUERY: {state['query']}
    
    RESULT:
    {state['message']}
    """
    return {"final_answer": formatted}


# Step 4: --------- Build the Graph ---------------------
graph = StateGraph(AgentState)

# Step 5: ---------------- Add nodes ----------------------
graph.add_node("node_classify", classify_question)
graph.add_node("node_account_lookup", accounting_lookup)
graph.add_node("node_account_assessment", accounting_assessment)
graph.add_node("node_collect_debt", collect_debt)
graph.add_node("node_account_good_standing", accounting_assessment_good)
graph.add_node("node_inventory_lookup", inventory_lookup)
graph.add_node("node_inventory_assessment", inventory_assessment)
graph.add_node("node_final_format", format_response)

# Step 5: ------------------- Set Entry point ----------------------------
graph.set_entry_point("node_classify")

# Step 6: -------------------- Create Edges to link Nodes ---------------------
# Conditional routing based on classification
def route(state: AgentState):
    return state["classification"]

graph.add_conditional_edges(
    "node_classify",                 # node
    route,                      # routing_function
    {                           # True : "node"
        "accounting": "node_account_lookup",
        "inventory": "node_inventory_lookup",
    }
)

# Accounting chain
graph.add_edge("node_account_lookup", "node_account_assessment")

def route2(state: AgentState):
    return state["llm_assessment"]

graph.add_conditional_edges(
    "node_account_assessment",                 # node
    route2,                      # routing_function
    {                           # True : "node"
        "low": "node_collect_debt",
        "acceptable": "node_account_good_standing",
    }
)

graph.add_edge("node_account_good_standing", "node_final_format")
graph.add_edge("node_collect_debt", "node_final_format")

# Inventory chain
graph.add_edge("node_inventory_lookup", "node_inventory_assessment")
graph.add_edge("node_inventory_assessment", "node_final_format")

# Step 8: ------------- Set End Node ---------------------
graph.add_edge("node_final_format", END)

# Step 9: ------------- Compile Graph ---------------------
app = graph.compile()

# Step 10: ----------------- Run Example -----------------------------
# Scenario 1: ask about Cash balance
print("#"*30)
result = app.invoke({"query": "What is the status of our cash balance?"})
print("\n=== RESPONSE 1 ===")
print(result["final_answer"])

# Scenario 2: ask about investment
print("#"*30)
result = app.invoke({"query": "check our payroll balance if adequet for a small shop?"})
print("\n=== RESPONSE 2 ===")
print(result["final_answer"])

# Scenario 3: ask about Inventory
print("#"*30)
result2 = app.invoke({"query": "Do we need to restock monitors?"})
print("\n=== RESPONSE 3 ===")
print(result2["final_answer"])

# Scenario 4: ask about Inventory
print("#"*30)
result2 = app.invoke({"query": "Do we need to restock keyboards?"})
print("\n=== RESPONSE 4 ===")
print(result2["final_answer"])