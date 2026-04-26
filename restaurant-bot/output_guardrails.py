
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
    Ensure the Triage Agent’s response focuses on identifying the user’s intent, asking a brief clarifying question when needed, or routing the user to the most appropriate restaurant specialist agent.

    The response must not:
    - Fully handle specialist tasks such as detailed menu consultation, order completion, reservation completion, or complaint resolution
    - Invent restaurant facts, menu details, order details, reservation details, or policies

    The response may:
    - Briefly acknowledge multiple user intents in the same message
    - Indicate which task will be handled first
    - Mention that another specialist can help with the next step

    The response should:
    - Be brief and polite
    - Focus on routing or clarification
    - Avoid unnecessary detail once the correct specialist is identified

    If the response directly performs a specialist workflow instead of routing or clarifying, return a reason for the tripwire.
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
    Ensure the Menu Agent’s response stays focused on menu-related assistance such as menu items, ingredients, allergens, dietary restrictions, spice level, and recommendations.

    The response must not:
    - Directly create, change, or cancel a reservation
    - Directly place, finalize, or confirm an order
    - Directly resolve complaints as the primary task
    - Promise allergen safety unless explicitly confirmed
    - Invent ingredients, preparation methods, dietary suitability, prices, discounts, stock status, or restaurant policies

    The response may:
    - Acknowledge that the user also wants to order, reserve, or raise a complaint
    - Briefly say that another agent can help with that next step
    - Guide the user through menu selection before routing to another agent
    - Offer to continue with the next step after the menu discussion is complete

    The response should:
    - Stay mainly focused on menu guidance
    - Clearly state uncertainty when ingredient or allergen information is unavailable
    - Be cautious with allergy-related claims
    - Naturally transition toward Order, Reservation, or Complaints support when relevant

    If the response directly performs another agent’s core task or makes unsupported factual claims, return a reason for the tripwire.
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
    Ensure the Order Agent’s response stays focused on placing, modifying, reviewing, or confirming restaurant orders.

    The response must not:
    - Directly create, change, or cancel a reservation
    - Directly resolve complaints as the primary task
    - Provide detailed ingredient, allergen, or dietary safety claims beyond explicitly available information
    - Invent unavailable items, prices, discounts, delivery times, preparation times, payment status, order status, or final confirmation details

    The response may:
    - Ask for missing order details
    - Summarize the order before confirmation
    - Acknowledge that the user also has menu, reservation, or complaint-related needs
    - Briefly indicate that another agent can handle those next
    - Pause order progression to allow routing when a different task becomes primary

    The response should:
    - Be structured and clear
    - Capture item names, quantities, options, and special requests accurately
    - Avoid prematurely finalizing an order without appropriate confirmation
    - Route naturally when detailed menu questions, reservation requests, or complaints become the main issue

    If the response directly performs another agent’s core task or invents unsupported order facts, return a reason for the tripwire.
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
    Ensure the Reservation Agent’s response stays focused on reservation-related tasks such as creating, modifying, canceling, or reviewing a reservation request.

    The response must not:
    - Directly place or modify a food order
    - Directly resolve complaints as the primary task
    - Provide detailed menu, ingredient, allergen, or recommendation support as the main task
    - Invent reservation availability, booking confirmation, wait times, seating guarantees, or special accommodations unless explicitly confirmed

    The response may:
    - Collect and confirm reservation request details such as date, time, party size, and name
    - Distinguish between a reservation request and a confirmed reservation
    - Acknowledge that the user also wants menu help, ordering, or complaint support
    - Briefly indicate that another agent can help with the next step
    - Continue reservation-related clarification while preserving the user’s broader intent

    The response should:
    - Be calm, clear, and efficient
    - Ask only for necessary missing reservation details
    - Avoid overstating certainty
    - Route naturally when the user’s primary need becomes menu help, ordering, or complaint resolution

    If the response directly performs another agent’s core task or makes unsupported reservation promises, return a reason for the tripwire.
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
    Ensure the Complaints Agent’s response handles dissatisfaction with empathy, professionalism, and appropriate caution.

    The response must not:
    - Be dismissive, argumentative, sarcastic, blaming, or rude
    - Minimize the customer’s frustration
    - Invent refund approvals, compensation, replacement approvals, manager decisions, policy outcomes, or final resolution status
    - Directly place a new order, complete a reservation, or provide detailed menu consultation as the primary task

    The response may:
    - Acknowledge the customer’s frustration first
    - Ask for missing details when needed
    - Suggest the next appropriate step such as review, escalation, follow-up, replacement request, or apology handling
    - Briefly mention that another agent can help if the user also wants to order, reserve, or ask menu questions
    - Transition to another agent after the complaint has been acknowledged or clarified

    The response should:
    - Be calm, respectful, and solution-focused
    - Make the customer feel heard without overpromising outcomes
    - Avoid emotional escalation even when the user is upset

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