from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import generate_page_image

MODEL = LiteLlm(model="openai/gpt-4o")


def create_image_generator_agent(page_number: int) -> Agent:
    return Agent(
        name=f"Page{page_number}ImageGeneratorAgent",
        description=f"Generates the illustration image for page {page_number}.",
        instruction=f"""
Your only task:
- Call generate_page_image with page_number={page_number}.
- Do not explain anything to the user.
- Do not display the image.
- Do not write story text.
- Return only the tool result as structured data.

This is an internal step. The final storybook will be presented by BookAssemblerAgent.
""",
        model=MODEL,
        tools=[generate_page_image],
        output_key=f"page_{page_number}_image_output",
    )