from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

system_prompt= """
 You are my first AI agent
"""

agent = create_agent(
    model="google_genai:gemini-flash-lite-latest",
    system_prompt=system_prompt,
    checkpointer=InMemorySaver()
)

thread_config = {"configurable": {"thread_id": "1"}}

def get_response(prompt: str) -> str:
    response = agent.invoke(
    {"messages": [prompt]},
    thread_config
    )
    return print(response["messages"][-1].text)



def main():
    while True:
        try:
            prompt = input("Input: ")
            if prompt == "exit": break
            response = get_response(prompt)
        except EOFError:
            break
        print(response)

if __name__ == "__main__":
    main()