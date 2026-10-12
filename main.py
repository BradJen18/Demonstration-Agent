import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai._function_utils").setLevel(logging.ERROR)
logging.disable(logging.WARNING)

import warnings
from langchain_core._api import LangChainBetaWarning
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.mcp import MCPAdapter
import asyncio

from rich.console import Console
from rich.markdown import Markdown
from Tools import get_weather,list_directory, read_safe_file, write_safe_file,add_memory

#Args:before each response, review the Ethics_folder.txt and decide if what you are doing aligns with the text. # additional prompt to add later
system_prompt= """
You are my up beat AI that corrects mistakes and doesn't sugar coat anything, but encourages personal growth and understanding

Args:
    Before each response, review the Ethics_document.txt and decide if what you are doing aligns with the text.
    Save relevant information to your memory.txt or user_profile.txt so that you have enough context to continue the conversation when your program starts again.


"""


def main():
    asyncio.run(_main())

async def _main(): #look up context7
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
    tools=mcp_tools+[get_weather,read_safe_file,list_directory,write_safe_file,add_memory],
    checkpointer=InMemorySaver()
    )

    thread_config = {"configurable": {"thread_id": "1"}}
    while True:
        print("\n-------- User ---------") #how do I make the user // AI indicators different colors?
        try:
            prompt = input("Input: ")
            if prompt == "exit": break
            response = await agent.ainvoke(
            {"messages": [prompt]}, thread_config
            )
        except EOFError:
            break
        print("\n--------- AI ----------")
        print(response["messages"][-1].text)

if __name__ == "__main__":
    main()