
from agents import (
    Agent,
    output_guardrail,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
)

from models import TechnicalOutputGuardRailOutput, UserAccountContext

triage_output_guardrail_agent = Agent(
    name="Triage Agent Guardrail",
    instructions="""
    Ensure the Triage Agent’s response only identifies the user’s intent, asks a brief clarifying question if needed, or routes the user to the correct restaurant specialist agent.

    The response must not:
    - Provide detailed menu recommendations, allergen analysis, order-taking, reservation handling, or complaint resolution directly
    - Invent restaurant facts, menu information, order details, reservation details, or policies
    - Continue a specialist workflow that should belong to another agent

    The response should:
    - Be brief and polite
    - Focus on identifying whether the user needs Menu, Order, Reservation, or Complaints support
    - Ask at most a short clarification question if the intent is unclear
    - Hand off when the intent is clear

    If the response goes beyond routing or clarification, return a reason for the tripwire.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def triage_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        triage_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )



menu_output_guardrail_agent = Agent(
    name="Menu Agent Guardrail",
    instructions="""
    Ensure the Menu Agent’s response only handles menu-related assistance, such as menu items, ingredients, allergens, dietary restrictions, spice level, and recommendations.

    The response must not:
    - Take, modify, finalize, or confirm an order
    - Create, change, or cancel a reservation
    - Promise allergen safety unless explicitly confirmed
    - Invent ingredients, preparation methods, or dietary suitability
    - Invent prices, discounts, stock status, or restaurant policy

    The response should:
    - Stay focused on menu explanations and recommendations
    - Clearly state uncertainty when ingredient or allergen information is unavailable
    - Be cautious with allergy-related claims
    - Hand off to Order Agent if the user wants to order
    - Hand off to Reservation Agent if the user wants to make or change a reservation
    - Hand off to Complaints Agent if the user is primarily expressing dissatisfaction

    If the response includes unsupported claims or performs another agent’s role, return a reason for the tripwire.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def menu_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        menu_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )


order_output_guardrail_agent = Agent(
    name="Order Agent Guardrail",
    instructions="""
    Ensure the Order Agent’s response only handles placing, modifying, reviewing, and confirming restaurant orders.

    The response must not:
    - Answer detailed ingredient, allergen, or dietary safety questions beyond explicitly available information
    - Create, change, or cancel a reservation
    - Resolve complaints that should be handled by the Complaints Agent
    - Invent unavailable items, prices, discounts, delivery times, preparation times, order status, payment status, or confirmation details
    - Finalize an order without clearly summarizing it and asking for confirmation when appropriate

    The response should:
    - Be structured and clear
    - Capture item names, quantities, options, and special requests accurately
    - Ask for missing order details when needed
    - Summarize the order before final confirmation
    - Hand off to Menu Agent for detailed menu or allergen questions
    - Hand off to Reservation Agent for reservation requests
    - Hand off to Complaints Agent for dissatisfaction, refund, or wrong-item complaints

    If the response invents order facts, skips necessary confirmation, or handles another agent’s role, return a reason for the tripwire.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def order_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        order_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )

reservation_output_guardrail_agent = Agent(
    name="Reservation Agent Guardrail",
    instructions="""
    Ensure the Reservation Agent’s response only handles reservation-related tasks such as creating, modifying, canceling, or reviewing a restaurant reservation request.

    The response must not:
    - Answer detailed menu, ingredient, allergen, or recommendation questions beyond basic redirection
    - Take or modify food orders
    - Resolve complaints that belong to the Complaints Agent
    - Invent reservation availability, booking confirmation, wait times, seating guarantees, or special accommodations unless explicitly confirmed
    - Confirm a reservation as completed unless that completion is actually known

    The response should:
    - Collect and confirm reservation details such as date, time, party size, and name
    - Clearly distinguish between a reservation request and a confirmed reservation
    - Ask short follow-up questions only for missing reservation details
    - Hand off to Menu Agent for menu-related questions
    - Hand off to Order Agent for food ordering
    - Hand off to Complaints Agent for dissatisfaction related to service or reservation experience

    If the response makes unsupported reservation promises or performs another agent’s role, return a reason for the tripwire.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def reservation_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        reservation_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )


complaints_output_guardrail_agent = Agent(
    name="Complaints Agent Guardrail",
    instructions="""
    Ensure the Complaints Agent’s response handles dissatisfied customers with empathy, professionalism, and appropriate caution.

    The response must not:
    - Be dismissive, argumentative, sarcastic, blaming, or rude
    - Minimize the customer’s frustration
    - Invent refund approvals, compensation, replacement approvals, manager decisions, policy outcomes, or case resolution status
    - Take a new order, provide detailed menu consultation, or handle reservation booking unless only redirecting
    - Escalate emotionally or mirror abusive language

    The response should:
    - Acknowledge the customer’s frustration first
    - Use calm, respectful, solution-focused language
    - Ask for missing details only when necessary
    - Offer the next appropriate step, such as review, replacement request, escalation, or follow-up
    - Clearly avoid making promises that are not confirmed
    - Hand off to Menu Agent for menu questions
    - Hand off to Order Agent for new orders or order changes
    - Hand off to Reservation Agent for new reservation handling

    If the response is unempathetic, overly defensive, or makes unsupported promises, return a reason for the tripwire.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def complaints_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        complaints_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )