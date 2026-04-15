from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

from openai import OpenAI
import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool

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
        ]
    )

agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession("chat-history", "chat-gpt-clone-memory.db")

session = st.session_state["session"]

async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])
        if "type" in message and message["type"] == "web_search_call":
            with st.chat_message("ai"):
                st.write(f"🔍 Web Search : \"{message["action"]["queries"][0]}\"")

def update_status(status_container, event):
    status_messages = {
        "response.web_search_call.completed": ("Web search completed.", "complete"),
        "response.web_search_call.searching": ("Web search in progress...", "running"),
        "response.web_search_call.in_progress": ("Starting web search...", "running"),

        "response.file_search_call.completed": ("File search completed.", "complete"),
        "response.file_search_call.searching": ("File search in progress...", "running"),
        "response.file_search_call.in_progress": ("Starting file search...", "running"),

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

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))

prompt = st.chat_input("Write a meessage",
                       accept_file=True,
                       file_type=["txt"]
                       )

if prompt:

    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("⏳ Uploadking file...") as status:
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


    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))
