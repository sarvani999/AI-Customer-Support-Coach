import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


SYSTEM_PROMPT = """
You are an AI Coaching and Response Suggestion Agent
for a Customer Support Coaching Assistant.

Your responsibilities are:

1. Generate a professional support-agent reply
   before the trainee submits a response.

2. Evaluate the trainee's submitted response.

3. Provide practical real-time coaching.

4. Identify strengths and communication improvements.

5. Use retrieved knowledge when it is available.

6. Evaluate:
   - empathy
   - tone
   - clarity
   - professionalism
   - policy accuracy
   - resolution quality

Rules:
- Never behave like the customer.
- Do not invent company policy.
- Return only valid JSON.
- Do not include markdown code blocks.
"""


class CoachingAgent:
    """
    Generates AI-based suggested replies
    and coaching feedback.
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


    def _clean_json_output(
        self,
        output_text
    ):
        """
        Removes optional markdown code fences
        before converting Gemini output to JSON.
        """

        output_text = str(
            output_text or ""
        ).strip()

        if output_text.startswith("```json"):
            output_text = output_text[
                len("```json"):
            ]

        elif output_text.startswith("```"):
            output_text = output_text[
                len("```"):
            ]

        if output_text.endswith("```"):
            output_text = output_text[:-3]

        return output_text.strip()


    def _normalize_score(
        self,
        value
    ):
        """
        Converts a score into an integer
        between 0 and 100.
        """

        try:
            score = int(value)

        except (
            TypeError,
            ValueError
        ):
            score = 0

        return max(
            0,
            min(
                100,
                score
            )
        )


    def _fallback_suggestion(
        self
    ):
        """
        Returns a safe suggested response
        when Gemini is unavailable.
        """

        return {
            "source": "fallback",
            "suggested_response": (
                "I am sorry for the inconvenience. "
                "I understand your concern. "
                "Please share the relevant order details "
                "so I can verify the issue and guide you "
                "through the next available steps."
            ),
            "reasoning": (
                "A safe fallback response was generated "
                "because the AI suggestion service "
                "was unavailable."
            )
        }

    def suggest_response(
        self,
        customer_message,
        customer_analysis=None,
        knowledge=None
    ):
        """
        Generates an AI suggested support reply
        before the trainee submits a response.
        """

        customer_message = str(
            customer_message or ""
        ).strip()

        customer_analysis = (
            customer_analysis or {}
        )

        knowledge = (
            knowledge or {}
        )

        if not customer_message:
            raise ValueError(
                "Customer message is required"
            )

        if not self.client:
            return self._fallback_suggestion()

        prompt = f"""
Customer Message:
{customer_message}

Customer Analysis:
{json.dumps(
    customer_analysis,
    ensure_ascii=False
)}

Retrieved Knowledge:
{json.dumps(
    knowledge,
    ensure_ascii=False
)}

Generate one professional customer-support agent reply.

Return only this JSON structure:

{{
  "source": "gemini",
  "suggested_response": "Generated support reply",
  "reasoning": "Short reason why this reply is suitable"
}}

Rules:
- Acknowledge the customer's emotion.
- Maintain a polite and professional tone.
- Give a clear next step.
- Use retrieved knowledge when available.
- Do not invent company policy.
- Keep the reply between 2 and 4 sentences.
- Return valid JSON only.
"""

        try:
            interaction = (
                self.client.interactions.create(
                    model="gemini-3.1-flash-lite",
                    system_instruction=SYSTEM_PROMPT,
                    input=prompt
                )
            )

            output_text = (
                self._clean_json_output(
                    interaction.output_text
                )
            )

            suggestion = json.loads(
                output_text
            )

            suggested_response = str(
                suggestion.get(
                    "suggested_response",
                    ""
                )
            ).strip()

            if not suggested_response:
                raise ValueError(
                    "Gemini returned an empty suggestion"
                )

            return {
                "source": suggestion.get(
                    "source",
                    "gemini"
                ),
                "suggested_response":
                    suggested_response,
                "reasoning": suggestion.get(
                    "reasoning",
                    ""
                )
            }

        except Exception as error:
            print(
                "GEMINI SUGGESTION ERROR =",
                error
            )

            return self._fallback_suggestion()


    def _fallback_feedback(
        self,
        customer_message,
        agent_reply,
        evaluation
    ):
        """
        Returns rule-based coaching when Gemini
        is unavailable or returns invalid output.
        """

        evaluation = evaluation or {}

        strengths = evaluation.get(
            "strengths",
            []
        )

        improvements = evaluation.get(
            "improvements",
            []
        )

        if not isinstance(
            strengths,
            list
        ):
            strengths = []

        if not isinstance(
            improvements,
            list
        ):
            improvements = []

        empathy_score = self._normalize_score(
            evaluation.get(
                "empathy_score",
                evaluation.get(
                    "empathy",
                    0
                )
            )
        )

        tone_score = self._normalize_score(
            evaluation.get(
                "tone_score",
                evaluation.get(
                    "tone",
                    0
                )
            )
        )

        clarity_score = self._normalize_score(
            evaluation.get(
                "clarity_score",
                evaluation.get(
                    "clarity",
                    0
                )
            )
        )

        professionalism_score = (
            self._normalize_score(
                evaluation.get(
                    "professionalism_score",
                    evaluation.get(
                        "professionalism",
                        0
                    )
                )
            )
        )

        policy_accuracy_score = (
            self._normalize_score(
                evaluation.get(
                    "policy_accuracy",
                    0
                )
            )
        )

        resolution_score = (
            self._normalize_score(
                evaluation.get(
                    "resolution_score",
                    evaluation.get(
                        "resolution",
                        0
                    )
                )
            )
        )

        if empathy_score < 70:
            suggested_response = (
                "I am sorry for the inconvenience, "
                "and I understand how frustrating "
                "this situation must be. "
                "Please share your order ID so I can "
                "check the issue and guide you through "
                "the next steps."
            )

        elif clarity_score < 70:
            suggested_response = (
                "I understand your concern. "
                "Please share your order ID. "
                "I will check the issue and explain "
                "the available resolution clearly."
            )

        elif tone_score < 70:
            suggested_response = (
                "Thank you for explaining the issue. "
                "I understand your concern, and I will "
                "help you with the next available steps."
            )

        else:
            suggested_response = (
                "I understand your concern. "
                "Please share your order ID so I can "
                "verify the details and help you with "
                "the appropriate resolution."
            )

        if not strengths:
            strengths = [
                "The trainee attempted to respond to the customer."
            ]

        if not improvements:
            improvements = [
                "Acknowledge the customer's concern clearly.",
                "Provide a specific and actionable next step."
            ]

        return {
            "source": "fallback",
            "suggested_response":
                suggested_response,
            "strengths":
                strengths,
            "improvement_tips":
                improvements,
            "reasoning": (
                "Fallback coaching was generated "
                "from the response evaluation scores."
            ),
            "scores": {
                "empathy":
                    empathy_score,
                "tone":
                    tone_score,
                "clarity":
                    clarity_score,
                "professionalism":
                    professionalism_score,
                "policy_accuracy":
                    policy_accuracy_score,
                "resolution":
                    resolution_score
            }
        }

    def generate_feedback(
        self,
        customer_message,
        agent_reply,
        customer_analysis=None,
        knowledge=None,
        evaluation=None
    ):
        """
        Generates AI-based coaching feedback
        after the trainee submits a response.
        """

        customer_message = str(
            customer_message or ""
        ).strip()

        agent_reply = str(
            agent_reply or ""
        ).strip()

        customer_analysis = (
            customer_analysis or {}
        )

        knowledge = (
            knowledge or {}
        )

        evaluation = (
            evaluation or {}
        )

        if not customer_message:
            raise ValueError(
                "Customer message is required"
            )

        if not agent_reply:
            raise ValueError(
                "Agent reply is required"
            )

        if not self.client:
            return self._fallback_feedback(
                customer_message,
                agent_reply,
                evaluation
            )

        prompt = f"""
Customer Message:
{customer_message}

Trainee Reply:
{agent_reply}

Customer Analysis:
{json.dumps(
    customer_analysis,
    ensure_ascii=False
)}

Retrieved Knowledge:
{json.dumps(
    knowledge,
    ensure_ascii=False
)}

Existing Evaluation:
{json.dumps(
    evaluation,
    ensure_ascii=False
)}

Evaluate the trainee reply.

Return only this JSON structure:

{{
  "source": "gemini",
  "suggested_response": "An improved support response",
  "strengths": [
    "Specific strength one",
    "Specific strength two"
  ],
  "improvement_tips": [
    "Specific improvement one",
    "Specific improvement two"
  ],
  "reasoning": "Short explanation of why the response should improve",
  "scores": {{
    "empathy": 0,
    "tone": 0,
    "clarity": 0,
    "professionalism": 0,
    "policy_accuracy": 0,
    "resolution": 0
  }}
}}

Rules:
- Every score must be an integer from 0 to 100.
- The suggested response must be realistic.
- Acknowledge the customer's emotion.
- Provide a clear next step.
- Use retrieved knowledge when available.
- Do not invent company policy.
- Keep strengths and improvement tips specific.
- Keep reasoning short.
- Return valid JSON only.
"""

        try:
            interaction = (
                self.client.interactions.create(
                    model="gemini-3.1-flash-lite",
                    system_instruction=SYSTEM_PROMPT,
                    input=prompt
                )
            )

            output_text = (
                self._clean_json_output(
                    interaction.output_text
                )
            )

            coaching = json.loads(
                output_text
            )

            if not isinstance(
                coaching,
                dict
            ):
                raise ValueError(
                    "Gemini coaching response is not a JSON object"
                )

            coaching.setdefault(
                "source",
                "gemini"
            )

            coaching.setdefault(
                "suggested_response",
                ""
            )

            coaching.setdefault(
                "strengths",
                []
            )

            coaching.setdefault(
                "improvement_tips",
                []
            )

            coaching.setdefault(
                "reasoning",
                ""
            )

            coaching.setdefault(
                "scores",
                {}
            )

            if not isinstance(
                coaching.get("strengths"),
                list
            ):
                coaching["strengths"] = []

            if not isinstance(
                coaching.get("improvement_tips"),
                list
            ):
                coaching["improvement_tips"] = []

            scores = coaching.get(
                "scores",
                {}
            )

            if not isinstance(
                scores,
                dict
            ):
                scores = {}

            coaching["scores"] = {
                "empathy": self._normalize_score(
                    scores.get(
                        "empathy",
                        0
                    )
                ),
                "tone": self._normalize_score(
                    scores.get(
                        "tone",
                        0
                    )
                ),
                "clarity": self._normalize_score(
                    scores.get(
                        "clarity",
                        0
                    )
                ),
                "professionalism": self._normalize_score(
                    scores.get(
                        "professionalism",
                        0
                    )
                ),
                "policy_accuracy": self._normalize_score(
                    scores.get(
                        "policy_accuracy",
                        0
                    )
                ),
                "resolution": self._normalize_score(
                    scores.get(
                        "resolution",
                        0
                    )
                )
            }

            coaching["suggested_response"] = str(
                coaching.get(
                    "suggested_response",
                    ""
                )
            ).strip()

            coaching["reasoning"] = str(
                coaching.get(
                    "reasoning",
                    ""
                )
            ).strip()

            return coaching

        except Exception as error:
            print(
                "GEMINI COACHING ERROR =",
                error
            )

            return self._fallback_feedback(
                customer_message,
                agent_reply,
                evaluation
            )