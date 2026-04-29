from google.adk.agents import ParallelAgent
from .prompt import PAGE_ASSET_GENERATOR_DESCRIPTION
from .image_generator.agent import create_image_generator_agent


page_asset_generator_agent = ParallelAgent(
    name="PageAssetGeneratorAgent",
    description=PAGE_ASSET_GENERATOR_DESCRIPTION,
    sub_agents=[
        create_image_generator_agent(page_number=1),
        create_image_generator_agent(page_number=2),
        create_image_generator_agent(page_number=3),
        create_image_generator_agent(page_number=4),
        create_image_generator_agent(page_number=5),
    ],
)