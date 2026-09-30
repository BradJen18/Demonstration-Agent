from dotenv import load_dotenv
import requests
import os
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
import asyncio

system_prompt= """
You are my british AI that loves to help, but is reluctant to work with me, an american
"""

@tool
def get_weather() -> str:
    """Get the weather for Rexburg, Idaho."""

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("Can't find API key in .env")

    lat, lon = 43.8231, -111.7924  # Rexburg, ID
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "units": "imperial","appid":api_key}

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    asyncio.run(_main())

async def _main():
    config = {
        "mcpServers": {
            "docs-langchain": {
            "url": "https://docs.langchain.com/mcp"
            },
            "reference-langchain": {
            "url": "https://reference.langchain.com/mcp"
            }
        }
    }

    async with MCPAdapter(config) as adapter:
        mcp_tools = await adapter.list_tools()

    agent = create_agent(
    model="google_genai:gemini-flash-lite-latest",
    system_prompt=system_prompt,
    tools=mcp_tools+[get_weather],
    checkpointer=InMemorySaver()
    )

    thread_config = {"configurable": {"thread_id": "1"}}
    while True:
        try:
            prompt = input("Input: ")
            if prompt == "exit": break
            response = await agent.ainvoke(
            {"messages": [prompt]}, thread_config
            )
        except EOFError:
            break
        print(response["messages"][-1].text)

if __name__ == "__main__":
    main()