import os
import random
import re

from dotenv import load_dotenv
from google import genai


load_dotenv()


SYSTEM_PROMPT = """
You are an AI Customer Simulator for a Customer Support Coaching Assistant.

Your role is to behave like a realistic customer speaking with a support agent.

Core responsibilities:
- Generate a natural customer message for every conversation turn.
- Continue from the previous conversation history.
- React directly to the support agent's latest reply.
- Stay focused on the selected support scenario.
- Maintain the selected customer persona and difficulty.
- Avoid repeating earlier customer messages.
- Ask realistic follow-up questions when the issue is unresolved.
- Show satisfaction only when the support response clearly resolves the issue.

Strict rules:
- Always behave only as the customer.
- Never behave as the support agent.
- Never provide coaching, evaluation, or policy explanations.
- Never mention prompts, AI, Gemini, or system instructions.
- Do not invent unrelated problems.
- Do not repeat the same wording from earlier turns.
- Keep each reply between 1 and 3 sentences.
- Reply only in the selected language.
- If Telugu is selected, use Telugu script.
- Return only the customer message.
- Do not use markdown, labels, quotation marks, or JSON.
"""


class CustomerSimulatorAgent:
    """
    Generates dynamic AI customer messages
    using Gemini and conversation history.
    """

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if api_key:

            self.client = genai.Client(
                api_key=api_key
            )

        else:

            self.client = None

        self.session_turns = {}

        self.session_messages = {}


    def reset_session(
        self,
        session_id
    ):
        """
        Clears turn count and generated-message
        history for one session.
        """

        session_key = str(
            session_id or "default"
        )

        if session_key in self.session_turns:

            del self.session_turns[
                session_key
            ]

        if session_key in self.session_messages:

            del self.session_messages[
                session_key
            ]


    def _get_turn_number(
        self,
        session_id
    ):
        """
        Returns and increments the turn number
        independently for each session.
        """

        session_key = str(
            session_id or "default"
        )

        current_turn = (
            self.session_turns.get(
                session_key,
                0
            ) + 1
        )

        self.session_turns[
            session_key
        ] = current_turn

        return current_turn


    def _get_previous_messages(
        self,
        session_id
    ):
        """
        Returns AI customer messages previously
        generated in the current session.
        """

        session_key = str(
            session_id or "default"
        )

        previous_messages = (
            self.session_messages.get(
                session_key,
                []
            )
        )

        if not isinstance(
            previous_messages,
            list
        ):

            previous_messages = []

        return previous_messages


    def _store_generated_message(
        self,
        session_id,
        message
    ):
        """
        Stores one generated customer message
        for repeat prevention.
        """

        session_key = str(
            session_id or "default"
        )

        clean_message = str(
            message or ""
        ).strip()

        if not clean_message:

            return

        previous_messages = (
            self._get_previous_messages(
                session_key
            )
        )

        previous_messages.append(
            clean_message
        )

        self.session_messages[
            session_key
        ] = previous_messages[-20:]

    def _normalize_message(
        self,
        message
    ):
        """
        Normalizes a message for repeat
        and similarity checking.
        """

        clean_message = str(
            message or ""
        ).strip().lower()

        clean_message = re.sub(
            r"\s+",
            " ",
            clean_message
        )

        clean_message = re.sub(
            r"[^a-z0-9\u0C00-\u0C7F ]",
            "",
            clean_message
        )

        return clean_message.strip()


    def _is_repeated_message(
        self,
        session_id,
        message
    ):
        """
        Checks whether the new message is the same
        or highly similar to an earlier message.
        """

        normalized_message = (
            self._normalize_message(
                message
            )
        )

        if not normalized_message:

            return True

        previous_messages = (
            self._get_previous_messages(
                session_id
            )
        )

        for previous_message in previous_messages:

            normalized_previous = (
                self._normalize_message(
                    previous_message
                )
            )

            if (
                normalized_message ==
                normalized_previous
            ):

                return True

            current_words = set(
                normalized_message.split()
            )

            previous_words = set(
                normalized_previous.split()
            )

            if (
                not current_words or
                not previous_words
            ):

                continue

            common_words = (
                current_words &
                previous_words
            )

            total_words = (
                current_words |
                previous_words
            )

            similarity = (
                len(common_words) /
                len(total_words)
            )

            if similarity >= 0.82:

                return True

        return False


    def _clean_ai_message(
        self,
        message
    ):
        """
        Cleans Gemini output and removes
        unwanted formatting or labels.
        """

        clean_message = str(
            message or ""
        ).strip()

        if clean_message.startswith(
            "```"
        ):

            clean_message = (
                clean_message
                .replace(
                    "```text",
                    "",
                    1
                )
                .replace(
                    "```",
                    "",
                    1
                )
            )

        if clean_message.endswith(
            "```"
        ):

            clean_message = (
                clean_message[:-3]
            )

        clean_message = clean_message.strip()

        unwanted_prefixes = [
            "customer:",
            "customer message:",
            "response:",
            "reply:"
        ]

        lower_message = (
            clean_message.lower()
        )

        for prefix in unwanted_prefixes:

            if lower_message.startswith(
                prefix
            ):

                clean_message = (
                    clean_message[
                        len(prefix):
                    ]
                    .strip()
                )

                break

        if (
            clean_message.startswith('"') and
            clean_message.endswith('"')
        ):

            clean_message = (
                clean_message[1:-1]
                .strip()
            )

        clean_message = re.sub(
            r"\s+",
            " ",
            clean_message
        )

        return clean_message.strip()


    def _format_history(
        self,
        conversation_history
    ):
        """
        Converts stored conversation turns
        into a Gemini-readable transcript.
        """

        if not conversation_history:

            return (
                "No previous conversation exists. "
                "Generate the opening customer message."
            )

        formatted_turns = []

        recent_turns = (
            conversation_history[-10:]
        )

        for index, turn in enumerate(
            recent_turns,
            start=1
        ):

            if not isinstance(
                turn,
                dict
            ):

                continue

            customer_message = str(
                turn.get(
                    "customer_message",
                    turn.get(
                        "customer",
                        ""
                    )
                )
            ).strip()

            agent_reply = str(
                turn.get(
                    "agent_reply",
                    turn.get(
                        "agent",
                        ""
                    )
                )
            ).strip()

            role = str(
                turn.get(
                    "role",
                    ""
                )
            ).strip().lower()

            message = str(
                turn.get(
                    "message",
                    ""
                )
            ).strip()

            if (
                role == "customer" and
                message
            ):

                formatted_turns.append(
                    f"Customer {index}: "
                    f"{message}"
                )

                continue

            if (
                role == "agent" and
                message
            ):

                formatted_turns.append(
                    f"Support Agent {index}: "
                    f"{message}"
                )

                continue

            if customer_message:

                formatted_turns.append(
                    f"Customer {index}: "
                    f"{customer_message}"
                )

            if agent_reply:

                formatted_turns.append(
                    f"Support Agent {index}: "
                    f"{agent_reply}"
                )

        if not formatted_turns:

            return (
                "No valid previous conversation exists. "
                "Generate the opening customer message."
            )

        return "\n".join(
            formatted_turns
        )


    def _get_latest_agent_reply(
        self,
        conversation_history
    ):
        """
        Returns the latest available
        support-agent reply.
        """

        if not conversation_history:

            return ""

        for turn in reversed(
            conversation_history
        ):

            if not isinstance(
                turn,
                dict
            ):

                continue

            agent_reply = str(
                turn.get(
                    "agent_reply",
                    ""
                )
            ).strip()

            if agent_reply:

                return agent_reply

            role = str(
                turn.get(
                    "role",
                    ""
                )
            ).strip().lower()

            message = str(
                turn.get(
                    "message",
                    ""
                )
            ).strip()

            if (
                role == "agent" and
                message
            ):

                return message

        return ""
    def _get_difficulty_instruction(
        self,
        difficulty
    ):
        """
        Returns behaviour instructions
        for the selected difficulty.
        """

        difficulty_name = str(
            difficulty or "Medium"
        ).strip().lower()

        difficulty_rules = {
            "easy": (
                "The customer should be calm, cooperative, "
                "and willing to provide details. "
                "The issue should be simple to resolve."
            ),
            "medium": (
                "The customer should have moderate concern, "
                "ask realistic follow-up questions, and expect "
                "a clear explanation or next step."
            ),
            "hard": (
                "The customer should be impatient, question vague "
                "answers, and require specific details before feeling satisfied."
            ),
            "expert": (
                "The customer should challenge unclear responses, "
                "refer to earlier statements, request precise timelines, "
                "and escalate naturally if the issue remains unresolved."
            )
        }

        return difficulty_rules.get(
            difficulty_name,
            difficulty_rules["medium"]
        )


    def _get_persona_instruction(
        self,
        persona
    ):
        """
        Returns conversation behaviour
        for the selected customer persona.
        """

        persona_name = str(
            persona or "Regular Customer"
        ).strip().lower()

        persona_rules = {
            "regular customer": (
                "Speak politely and directly. "
                "Ask normal follow-up questions."
            ),
            "calm": (
                "Remain patient, polite, and cooperative."
            ),
            "frustrated": (
                "Show clear frustration, but remain understandable "
                "and focused on resolving the issue."
            ),
            "angry": (
                "Use a firm and upset tone. "
                "Demand a clear solution and avoid accepting vague answers."
            ),
            "confused": (
                "Ask for clarification and mention uncertainty "
                "about what to do next."
            ),
            "impatient": (
                "Ask for quick action, clear timelines, "
                "and avoid long explanations."
            ),
            "loyal customer": (
                "Mention being a regular customer and express "
                "disappointment that the current experience is poor."
            ),
            "new customer": (
                "Ask basic questions and show limited knowledge "
                "of the support process."
            )
        }

        return persona_rules.get(
            persona_name,
            (
                "Behave consistently with the selected persona "
                "and respond naturally."
            )
        )


    def _scenario_fallbacks(
        self,
        product,
        scenario,
        persona,
        latest_agent_reply="",
        turn=1
    ):
        """
        Returns context-aware fallback messages
        when Gemini is unavailable.
        """

        scenario_name = str(
            scenario or ""
        ).strip().lower()

        persona_name = str(
            persona or ""
        ).strip().lower()

        product_name = str(
            product or "the product"
        ).strip()

        latest_reply = str(
            latest_agent_reply or ""
        ).strip().lower()

        opening_messages = {
            "return request": [
                (
                    f"I want to return my {product_name} order. "
                    "Could you explain the return process?"
                ),
                (
                    "The item does not match what I expected, "
                    "so I would like to return it."
                ),
                (
                    "I tried to create a return request, "
                    "but the option is not working."
                )
            ],
            "refund request": [
                (
                    "I returned the product, but I still "
                    "have not received my refund."
                ),
                (
                    "The return was completed several days ago. "
                    "When will the money be credited?"
                ),
                (
                    "The refund status is still pending. "
                    "Could you please check it?"
                )
            ],
            "wrong product": [
                (
                    "I ordered one product, but the package "
                    "contains a completely different item."
                ),
                (
                    "The item I received does not match "
                    "the product shown in my order."
                ),
                (
                    "I received the wrong item and need "
                    "the correct product sent to me."
                )
            ],
            "damaged product": [
                (
                    "The product arrived damaged, "
                    "and I need a replacement."
                ),
                (
                    "The package was damaged, and the item "
                    "inside is also broken."
                ),
                (
                    "The product was already cracked "
                    "when I opened the box."
                )
            ],
            "late delivery": [
                (
                    "My order was supposed to arrive already, "
                    "but it has still not been delivered."
                ),
                (
                    "The expected delivery date has passed. "
                    "Can you check the status?"
                ),
                (
                    "The tracking information has not changed "
                    "for several days."
                )
            ],
            "order cancellation": [
                (
                    "I want to cancel my order before "
                    "it is shipped."
                ),
                (
                    "The cancellation option is not available. "
                    "Can you help me?"
                ),
                (
                    "I placed this order by mistake "
                    "and need to cancel it."
                )
            ],
            "payment issue": [
                (
                    "The payment was deducted, but my order "
                    "was not confirmed."
                ),
                (
                    "I was charged twice for the same order."
                ),
                (
                    "The transaction succeeded, but the order "
                    "still shows payment pending."
                )
            ],
            "missing item": [
                (
                    "One of the items from my order "
                    "is missing from the package."
                ),
                (
                    "The package arrived, but it did not contain "
                    "everything I ordered."
                ),
                (
                    "The invoice lists the item, "
                    "but it was not inside the box."
                )
            ],
            "exchange request": [
                (
                    "I need to exchange this item "
                    "for a different size."
                ),
                (
                    "Could you help me replace this product "
                    "with another variant?"
                ),
                (
                    "I want an exchange instead of a refund."
                )
            ]
        }

        follow_up_messages = [
            (
                "Could you please give me a clear timeline "
                "for when this will be resolved?"
            ),
            (
                "What exact information do you need from me "
                "to continue with this request?"
            ),
            (
                "I understand, but that still does not explain "
                "what happens next."
            ),
            (
                "Can you confirm whether this issue can be "
                "resolved today?"
            ),
            (
                "I already explained the problem. "
                "Please tell me the next specific step."
            )
        ]

        if any(
            phrase in latest_reply
            for phrase in [
                "order id",
                "order number",
                "reference number",
                "transaction id"
            ]
        ):

            follow_up_messages.extend([
                (
                    "I can provide the order details. "
                    "What will you check after I share them?"
                ),
                (
                    "I have the order ID ready. "
                    "How long will the verification take?"
                )
            ])

        if any(
            phrase in latest_reply
            for phrase in [
                "wait",
                "business days",
                "working days",
                "processing time"
            ]
        ):

            follow_up_messages.extend([
                (
                    "I have already waited several days. "
                    "Why is it taking longer than expected?"
                ),
                (
                    "Can you give me the exact date "
                    "instead of a general waiting period?"
                )
            ])

        if any(
            phrase in latest_reply
            for phrase in [
                "sorry",
                "apologize",
                "apologies"
            ]
        ):

            follow_up_messages.extend([
                (
                    "I appreciate the apology, "
                    "but what action will be taken now?"
                ),
                (
                    "Thank you, but I still need "
                    "a clear resolution."
                )
            ])

        if turn <= 1:

            messages = opening_messages.get(
                scenario_name,
                [
                    (
                        f"I am having a problem with my "
                        f"{product_name} order."
                    ),
                    (
                        "I need help resolving an issue "
                        "with my recent order."
                    ),
                    (
                        "My support issue is still unresolved. "
                        "Could you please check it?"
                    )
                ]
            )

        else:

            messages = follow_up_messages

        if persona_name == "angry":

            messages = [
                f"This is unacceptable. {message}"
                for message in messages
            ]

        elif persona_name == "frustrated":

            messages = [
                (
                    "This is becoming very frustrating. "
                    f"{message}"
                )
                for message in messages
            ]

        elif persona_name == "confused":

            messages = [
                (
                    "I am still confused. "
                    f"{message}"
                )
                for message in messages
            ]

        elif persona_name == "impatient":

            messages = [
                (
                    "I need this resolved quickly. "
                    f"{message}"
                )
                for message in messages
            ]

        return messages

    def _choose_fallback_message(
        self,
        session_id,
        fallback_messages
    ):
        """
        Chooses a fallback message that has not
        already been used in the current session.
        """

        available_messages = [
            message
            for message in fallback_messages
            if not self._is_repeated_message(
                session_id,
                message
            )
        ]

        if available_messages:

            return random.choice(
                available_messages
            )

        return random.choice(
            fallback_messages
        )


    def generate_message(
        self,
        product,
        scenario,
        persona,
        language="English",
        difficulty="Medium",
        conversation_history=None,
        session_id="default"
    ):
        """
        Generates a new AI customer message
        using conversation history and session context.
        """

        conversation_history = (
            conversation_history or []
        )

        turn = self._get_turn_number(
            session_id
        )

        history = self._format_history(
            conversation_history
        )

        latest_agent_reply = (
            self._get_latest_agent_reply(
                conversation_history
            )
        )

        previous_messages = (
            self._get_previous_messages(
                session_id
            )
        )

        persona_instruction = (
            self._get_persona_instruction(
                persona
            )
        )

        difficulty_instruction = (
            self._get_difficulty_instruction(
                difficulty
            )
        )

        fallback_messages = (
            self._scenario_fallbacks(
                product=product,
                scenario=scenario,
                persona=persona,
                latest_agent_reply=
                    latest_agent_reply,
                turn=turn
            )
        )

        if not self.client:

            fallback_message = (
                self._choose_fallback_message(
                    session_id,
                    fallback_messages
                )
            )

            self._store_generated_message(
                session_id,
                fallback_message
            )

            return fallback_message

        previous_messages_text = (
            "\n".join(
                [
                    f"- {message}"
                    for message
                    in previous_messages[-12:]
                ]
            )
            or "No previous AI-generated messages."
        )

        latest_agent_reply_text = (
            latest_agent_reply
            or "No support-agent reply exists yet."
        )

        prompt = f"""
Product:
{product}

Scenario:
{scenario}

Customer Persona:
{persona}

Persona Behaviour:
{persona_instruction}

Difficulty:
{difficulty}

Difficulty Behaviour:
{difficulty_instruction}

Language:
{language}

Conversation Turn:
{turn}

Conversation History:
{history}

Latest Support Agent Reply:
{latest_agent_reply_text}

Previously Generated Customer Messages:
{previous_messages_text}

Generate only the customer's next message.

Important requirements:
- Continue directly from the latest support-agent reply.
- If this is the opening turn, clearly introduce the selected issue.
- If the agent asks for information, respond realistically or ask what happens after sharing it.
- If the agent gives a vague answer, ask for a specific action or timeline.
- If the agent apologizes without giving a solution, acknowledge it but request action.
- If the agent provides a useful next step, respond naturally without pretending the issue is already resolved.
- If the issue is clearly resolved, show reasonable satisfaction and confirmation.
- Stay strictly within the selected scenario.
- Follow the selected persona and difficulty.
- Do not copy or closely repeat any previous customer message.
- Use different wording and sentence structure from earlier turns.
- Keep the response between 1 and 3 sentences.
- Reply only in {language}.
- Return only the customer message.
"""

        generation_attempts = 3

        for attempt in range(
            generation_attempts
        ):

            try:

                interaction = (
                    self.client.interactions.create(
                        model=(
                            "gemini-3.1-flash-lite"
                        ),
                        system_instruction=(
                            SYSTEM_PROMPT
                        ),
                        input=prompt
                    )
                )

                message = (
                    self._clean_ai_message(
                        interaction.output_text
                    )
                )

                if not message:

                    print(
                        "CUSTOMER SIMULATOR EMPTY OUTPUT "
                        f"ON ATTEMPT {attempt + 1}"
                    )

                    continue

                if self._is_repeated_message(
                    session_id,
                    message
                ):

                    print(
                        "CUSTOMER SIMULATOR REPEATED OUTPUT "
                        f"ON ATTEMPT {attempt + 1}"
                    )

                    prompt += f"""

The previous generated response was too similar
to an earlier customer message.

Generate a clearly different follow-up message.
Do not repeat this message:
{message}
"""

                    continue

                self._store_generated_message(
                    session_id,
                    message
                )

                return message

            except Exception as error:

                print(
                    "CUSTOMER SIMULATOR ERROR "
                    f"ON ATTEMPT {attempt + 1} =",
                    error
                )

        fallback_message = (
            self._choose_fallback_message(
                session_id,
                fallback_messages
            )
        )

        self._store_generated_message(
            session_id,
            fallback_message
        )

        return fallback_message