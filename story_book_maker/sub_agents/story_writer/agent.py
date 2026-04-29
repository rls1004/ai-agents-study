from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import STORY_WRITER_DESCRIPTION, STORY_WRITER_PROMPT

from pydantic import BaseModel, Field
from typing import List


class CharacterOutput(BaseModel):
    name: str = Field(description="Character name")
    description: str = Field(
        description="Consistent visual description of the character"
    )


class PageOutput(BaseModel):
    page_number: int = Field(description="Page number from 1 to 5")
    text: str = Field(
        description="Child-friendly story text for this page"
    )
    visual_description: str = Field(
        description="Detailed illustration description for this page"
    )
    characters: List[str] = Field(
        description="Names of characters appearing on this page"
    )
    setting: str = Field(
        description="Where the scene takes place"
    )
    mood: str = Field(
        description="Emotional tone of the page"
    )


class StoryWriterOutput(BaseModel):
    theme: str = Field(description="The user-provided story theme")
    title: str = Field(description="Title of the children’s storybook")
    target_age: str = Field(
        description="Target age range for the story, e.g. 4-7"
    )
    art_style: str = Field(
        description="Overall illustration style for the book"
    )
    characters: List[CharacterOutput] = Field(
        description="Main characters with consistent visual descriptions"
    )
    pages: List[PageOutput] = Field(
        description="Exactly 5 storybook pages"
    )


MODEL = LiteLlm(model="openai/gpt-4o")

story_writer_agent = Agent(
    name="StoryWriterAgent",
    description=STORY_WRITER_DESCRIPTION,
    instruction=STORY_WRITER_PROMPT,
    model=MODEL,
    output_schema=StoryWriterOutput,
    output_key="story_writer_output",
)