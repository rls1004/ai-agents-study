from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / ".env")

import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="""
        You are a helpful life coach. You always gather information through web searches before giving advice.

        You have access to the following tools:
            - Web Search Tool: Use this when the user asks a questions. Use this to learn about current evetns.
        """,
        tools=[
            WebSearchTool(),
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

prompt = st.chat_input("Write a meessage")

if prompt:
    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))
