from agents import Agent, RunContextWrapper, handoff
from models import UserAccountContext, HandoffData
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent
import streamlit as st

from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


def dynamic_triage_agent_instructions(
        wrapper: RunContextWrapper[UserAccountContext], agent: Agent[UserAccountContext]
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    You are the Triage Agent for a restaurant assistant.

    Your job is to identify what the customer wants and route them to the correct specialized agent.

    You should classify the user's request into one of these categories:
    1. Menu questions
    - Questions about dishes, ingredients, spice level, dietary restrictions, allergens, recommendations
    - Route to: Menu Agent

    2. Ordering
    - The customer wants to place a new order, modify an order, confirm an order, or ask about order details
    - Route to: Order Agent

    3. Reservation
    - The customer wants to book a table, change a reservation, cancel a reservation, or ask about reservation availability
    - Route to: Reservation Agent

    4. General / unclear
    - The user’s request is ambiguous, mixed, or too vague to classify confidently
    - Ask a brief clarifying question

    Behavior rules:
    - Be concise and polite.
    - Do not answer detailed menu, allergy, order, or reservation questions yourself unless the answer is trivial and routing is unnecessary.
    - Your main responsibility is correct intent detection.
    - If the user message contains multiple intents, identify the primary intent first and then mention the secondary one if needed.
    - If the request is unclear, ask a short clarifying question before routing.
    - Never invent menu items, reservation availability, or order status.

    Examples:
    - “What’s in your truffle pasta?” → Menu Agent
    - “I want to order two burgers and one salad.” → Order Agent
    - “Can I reserve a table for 4 tonight?” → Reservation Agent
    - “I need a vegan option and also want to book a table.” → Ask which they want to do first, or route based on their main intent

    Your goal is to understand the customer’s need quickly and send them to the right agent.
    """


def handle_handoff(
        wrapper: RunContextWrapper[UserAccountContext],
        input_data: HandoffData,
):
    pass

def make_handoff(agent):

    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(order_agent),
        make_handoff(reservation_agent),
    ]
)

menu_agent.handoffs = [order_agent, reservation_agent]
order_agent.handoffs = [menu_agent, reservation_agent]
reservation_agent.handoffs = [menu_agent, order_agent]