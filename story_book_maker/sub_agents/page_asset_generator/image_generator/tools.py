import base64
from openai import OpenAI
from google.adk.tools.tool_context import ToolContext

client = OpenAI()


async def generate_page_image(tool_context: ToolContext, page_number: int) -> dict:
    story = tool_context.state.get("story_writer_output", {})
    pages = story.get("pages", [])

    page = next((p for p in pages if p.get("page_number") == page_number), None)
    if not page:
        return {"status": "error", "message": f"page {page_number} not found"}

    prompt = f"""
Create one illustration for page {page_number} of a Korean children's storybook.

Art style:
{story.get("art_style")}

Characters:
{story.get("characters")}

Page visual description:
{page.get("visual_description")}

Setting:
{page.get("setting")}

Mood:
{page.get("mood")}

Do not include text, letters, captions, or speech bubbles.
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        quality="low",
        moderation="low",
        output_format="jpeg",
        background="opaque",
        size="1024x1024",
    )

    image_b64 = result.data[0].b64_json

    # 중요: 여기서는 save_artifact 하지 않음
    tool_context.state[f"page_{page_number}_image_b64"] = image_b64

    return {
        "status": "complete",
        "page_number": page_number,
        "state_key": f"page_{page_number}_image_b64",
    }