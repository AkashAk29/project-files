from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# --------------------------------------------------
# 1. Define the state
# --------------------------------------------------

class AgentState(TypedDict):
    user_request: str
    action: str
    approved: bool
    result: str


# --------------------------------------------------
# 2. Node 1 - Analyze request
# --------------------------------------------------

def analyze_request(state: AgentState):

    print("\n🤖 Agent: Analyzing request...")

    # Pretend an LLM decided what action to take
    action = "Delete important_file.txt"

    return {
        "action": action
    }


# --------------------------------------------------
# 3. Node 2 - Human approval
# --------------------------------------------------

def human_approval(state: AgentState):

    print("\n🤖 Agent wants to perform:")
    print(f"   {state['action']}")

    # -------------------------------
    # PAUSE HERE
    # -------------------------------

    decision = interrupt(
        {
            "message": "Human approval required",
            "action": state["action"]
        }
    )

    # Execution continues here ONLY
    # after Command(resume=...) is provided

    print(f"\n🤖 Human responded: {decision}")

    return {
        "approved": decision == "yes"
    }


# --------------------------------------------------
# 4. Node 3 - Execute action
# --------------------------------------------------

def execute_action(state: AgentState):

    if state["approved"]:

        print("\n🤖 Executing action...")

        return {
            "result": f"SUCCESS: {state['action']}"
        }

    else:

        print("\n🤖 Action rejected.")

        return {
            "result": "Action rejected by human."
        }


# --------------------------------------------------
# 5. Build graph
# --------------------------------------------------

builder = StateGraph(AgentState)

builder.add_node("analyze_request", analyze_request)
builder.add_node("human_approval", human_approval)
builder.add_node("execute_action", execute_action)

builder.add_edge(START, "analyze_request")
builder.add_edge("analyze_request", "human_approval")
builder.add_edge("human_approval", "execute_action")
builder.add_edge("execute_action", END)


# --------------------------------------------------
# 6. Create checkpointer
# --------------------------------------------------

checkpointer = InMemorySaver()


# --------------------------------------------------
# 7. Compile graph
# --------------------------------------------------

app = builder.compile(
    checkpointer=checkpointer
)


# --------------------------------------------------
# 8. Start workflow
# --------------------------------------------------

thread_id = "user-123"

config = {
    "configurable": {
        "thread_id": thread_id
    }
}


print("\n==============================")
print("   HUMAN-IN-THE-LOOP AGENT")
print("==============================")

initial_state = {
    "user_request": "Delete the important file",
    "action": "",
    "approved": False,
    "result": ""
}


# --------------------------------------------------
# First execution
# --------------------------------------------------

print("\n🚀 Starting agent...\n")

result = app.invoke(
    initial_state,
    config=config
)


# --------------------------------------------------
# Check if workflow was interrupted
# --------------------------------------------------

print("\n==============================")
print("Workflow interrupted!")
print("==============================")

print("\nInterrupt information:")

for interruption in result["__interrupt__"]:
    print(interruption.value)


# --------------------------------------------------
# Human-in-the-loop
# --------------------------------------------------

human_input = input(
    "\n👤 Approve action? Type 'yes' or 'no': "
).strip().lower()


# --------------------------------------------------
# Resume the SAME workflow
# --------------------------------------------------

result = app.invoke(
    Command(resume=human_input),
    config=config
)


# --------------------------------------------------
# Final result
# --------------------------------------------------

print("\n==============================")
print("Workflow completed")
print("==============================")

print(result)