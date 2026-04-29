import base64
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def assemble_storybook(tool_context: ToolContext) -> dict:
    story = tool_context.state.get("story_writer_output", {})
    pages = story.get("pages", [])

    if not pages:
        return {
            "status": "error",
            "storybook_text": "story_writer_output.pages를 찾을 수 없습니다.",
        }

    pages = sorted(pages, key=lambda p: p.get("page_number", 0))

    lines = [f"# {story.get('title', '동화책')}", ""]

    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text", "")

        lines.append(f"## {page_number}페이지")
        lines.append(text)
        lines.append("")

        image_b64 = tool_context.state.get(f"page_{page_number}_image_b64")
        if image_b64:
            image_bytes = base64.b64decode(image_b64)
            filename = f"page_{page_number}_image.jpeg"

            artifact = types.Part(
                inline_data=types.Blob(
                    mime_type="image/jpeg",
                    data=image_bytes,
                )
            )

            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact,
            )

        lines.append("")

    return {
        "status": "success",
        "storybook_text": "\n".join(lines),
    }