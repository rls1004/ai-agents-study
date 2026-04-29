from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import assemble_storybook

MODEL = LiteLlm(model="openai/gpt-4o")

book_assembler_agent = Agent(
    name="BookAssemblerAgent",
    model=MODEL,
    description="Assembles the final Korean storybook and saves all generated page images at the final step.",
    instruction="""
Call assemble_storybook.

After the tool returns, print only storybook_text.
Do not print JSON.
Do not mention image filenames.
Do not explain the workflow.
""",
    tools=[assemble_storybook],
)