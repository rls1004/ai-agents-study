from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.adk.models.lite_llm import LiteLlm

from .sub_agents.story_writer.agent import story_writer_agent
from .sub_agents.page_asset_generator.agent import page_asset_generator_agent
from .sub_agents.book_assembler.agent import book_assembler_agent

from google.adk.agents import SequentialAgent

from .prompt import BOOK_PRODUCER_DESCRIPTION, BOOK_PRODUCER_PROMPT

MODEL = LiteLlm(model="openai/gpt-4o")


book_producer_agent = SequentialAgent(
    name="BookProducerAgent",
    # model=MODEL,
    description=BOOK_PRODUCER_DESCRIPTION,
    # instruction=BOOK_PRODUCER_PROMPT,
    # tools=[
    #     AgentTool(agent=story_writer_agent),
    #     AgentTool(agent=page_asset_generator_agent),
    #     AgentTool(agent=book_assembler_agent),
    # ],
    sub_agents=[
        story_writer_agent,
        page_asset_generator_agent,
        book_assembler_agent,
    ],
)

root_agent = book_producer_agent