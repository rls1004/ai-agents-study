from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

import base64, copy
from openai import OpenAI
import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool, ImageGenerationTool

class SafeSQLiteSession(SQLiteSession):
    async def add_items(self, items):
        def sanitize(obj):
            if isinstance(obj, dict):
                new_obj = {}
                for k, v in obj.items():
                    if k == "action":
                        continue
                    new_obj[k] = sanitize(v)
                return new_obj
            elif isinstance(obj, list):
                return [sanitize(x) for x in obj]
            return obj

        safe_items = sanitize(copy.deepcopy(items))
        return await super().add_items(safe_items)

client = OpenAI()

VECTOR_STORE_ID = "vs_69dfab66a8fc8191baa892edfdf67229"

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="""
        You are a helpful life coach.

        Tool usage rules:
        - DO NOT use any tools for simple greetings, casual conversation, or small talk (e.g., "hi", "hello", "how are you").
        - Use Web Search when the user asks about:
        - prices, recommendations, places, trends, or general knowledge
        - anything that may require up-to-date or external information
        - Use File Search only when the question is clearly about the user's personal data or uploaded files.
        - If both are useful, use File Search first, then Web Search.

        You have access to the following tools:
            - Web Search Tool: Use this when the user asks some information.
            - File Search Tool: Use this tool when the user asks a question about facts related to themselves. Or when they ask questions about specific files.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[
                    VECTOR_STORE_ID
                ],
                max_num_results=3,
            ),
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "low",
                    "output_format": "jpeg",
                    "moderation": "low",
                    "partial_images": 1
                }
            )
        ]
    )

agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SafeSQLiteSession("chat-history", "chat-gpt-clone-memory.db")

session = st.session_state["session"]

async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.write(part["image_url"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])
        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write(f"🔍 Searched web")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("Searched your files...")
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image)

def update_status(status_container, event):
    status_messages = {
        "response.web_search_call.completed": ("Web search completed.", "complete"),
        "response.web_search_call.searching": ("Web search in progress...", "running"),
        "response.web_search_call.in_progress": ("Starting web search...", "running"),

        "response.file_search_call.completed": ("File search completed.", "complete"),
        "response.file_search_call.searching": ("File search in progress...", "running"),
        "response.file_search_call.in_progress": ("Starting file search...", "running"),

        "response.image_generation_call.generating": ("Drawing image...", "running"),
        "response.image_generation_call.in_progress": ("Drawing image...", "running"),

        "response.completed": ("", "complete")

    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


asyncio.run(paint_history())

async def run_agent(message):
    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        image_placeholer = st.empty()
        response = ""

        stream = Runner.run_streamed(
            agent,
            message,
            session=session
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)
                elif event.data.type == "response.image_generation_call.partial_image":
                    image = base64.b64decode(event.data.partial_image_b64)
                    image_placeholer.image(image)

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))

prompt = st.chat_input("Write a meessage",
                       accept_file=True,
                       file_type=["txt", "jpg", "jpeg", "png"],
                       )

if prompt:

    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data"
                    )
                    status.update(label="⏳ Attaching file...")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id
                    )
                    status.update(label="✅ File uploaded", state="complete")
        elif file.type.startswith("image/"):
            with st.status("⏳ Uploading image...") as status:
                file_bytes = file.getvalue()
                base64_data = base64.b64encode(file_bytes).decode("utf-8")
                data_uri = f"data:${file.type};base64,{base64_data}"
                asyncio.run(
                    session.add_items(
                        [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_image",
                                        "detail": "auto",
                                        "image_url": data_uri,
                                    }
                                ]
                            }
                        ]
                    )
                )
                status.update(label="✅ Image uploaded", state="complete")
            with st.chat_message("human"):
                st.image(data_uri)


    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))
