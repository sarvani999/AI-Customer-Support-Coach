import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


SYSTEM_PROMPT = """
You are a Post-Interaction Summary Agent
for an AI Customer Support Coaching Assistant.

Your responsibility is to analyze a completed
customer-support training session.

Generate:

1. A concise interaction summary.
2. Customer sentiment journey across the conversation.
3. Resolution quality score.
4. Final customer outcome.
5. Key strengths shown by the trainee.
6. Personalized coaching recommendations.
7. Important knowledge gaps when visible.

Rules:
- Use only the supplied conversation data.
- Do not invent customer or company information.
- Keep recommendations practical and specific.
- Return valid JSON only.
- Do not include markdown code blocks.
"""


class PostInteractionSummaryAgent:
    """
    Generates final AI-based analysis
    after a customer-support session ends.
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
        from Gemini output.
        """

        output_text = str(
            output_text or ""
        ).strip()

        if output_text.startswith(
            "```json"
        ):

            output_text = output_text[
                len("```json"):
            ]

        elif output_text.startswith(
            "```"
        ):

            output_text = output_text[
                len("```"):
            ]

        if output_text.endswith(
            "```"
        ):

            output_text = (
                output_text[:-3]
            )

        return output_text.strip()


    def _normalize_score(
        self,
        value
    ):
        """
        Keeps numerical scores
        between 0 and 100.
        """

        try:

            score = int(
                round(
                    float(value)
                )
            )

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


    def _get_sentiment_journey(
        self,
        turns
    ):
        """
        Creates a structured sentiment journey
        using existing customer analysis.
        """

        journey = []

        for turn in turns:

            analysis = (
                turn.get(
                    "customer_analysis",
                    {}
                ) or {}
            )

            journey.append({

                "turn":
                    turn.get(
                        "turn_number",
                        len(journey) + 1
                    ),

                "sentiment":
                    analysis.get(
                        "sentiment",
                        "Unknown"
                    ),

                "frustration":
                    analysis.get(
                        "frustration_level",
                        "Unknown"
                    ),

                "intent":
                    analysis.get(
                        "intent",
                        "Unknown"
                    )

            })

        return journey


    def _calculate_resolution_score(
        self,
        turns,
        existing_summary
    ):
        """
        Calculates a reliable resolution
        quality score from stored evaluations.
        """

        if not turns:

            return 0

        summary_score = (
            existing_summary.get(
                "average_resolution",
                0
            )
        )

        if summary_score:

            return self._normalize_score(
                summary_score
            )

        resolution_scores = []

        for turn in turns:

            evaluation = (
                turn.get(
                    "evaluation",
                    {}
                ) or {}
            )

            score = evaluation.get(
                "resolution_score",
                evaluation.get(
                    "resolution",
                    0
                )
            )

            try:

                resolution_scores.append(
                    float(score)
                )

            except (
                TypeError,
                ValueError
            ):

                continue

        if not resolution_scores:

            return 0

        average_score = (
            sum(resolution_scores)
            /
            len(resolution_scores)
        )

        return self._normalize_score(
            average_score
        )


    def _collect_strengths(
        self,
        turns
    ):
        """
        Collects unique strengths from
        all turn evaluations.
        """

        strengths = []

        for turn in turns:

            evaluation = (
                turn.get(
                    "evaluation",
                    {}
                ) or {}
            )

            items = evaluation.get(
                "strengths",
                []
            )

            if not isinstance(
                items,
                list
            ):

                continue

            for item in items:

                clean_item = str(
                    item or ""
                ).strip()

                if (
                    clean_item
                    and
                    clean_item
                    not in strengths
                ):

                    strengths.append(
                        clean_item
                    )

        return strengths


    def _collect_improvements(
        self,
        turns
    ):
        """
        Collects unique improvement points
        from all turn evaluations.
        """

        improvements = []

        for turn in turns:

            evaluation = (
                turn.get(
                    "evaluation",
                    {}
                ) or {}
            )

            items = evaluation.get(
                "improvements",
                evaluation.get(
                    "improvement_tips",
                    []
                )
            )

            if not isinstance(
                items,
                list
            ):

                continue

            for item in items:

                clean_item = str(
                    item or ""
                ).strip()

                if (
                    clean_item
                    and
                    clean_item
                    not in improvements
                ):

                    improvements.append(
                        clean_item
                    )

        return improvements


    def _fallback_summary(
        self,
        session,
        existing_summary
    ):
        """
        Creates a rule-based final summary
        when Gemini is unavailable.
        """

        turns = session.get(
            "turns",
            []
        )

        sentiment_journey = (
            self._get_sentiment_journey(
                turns
            )
        )

        resolution_score = (
            self._calculate_resolution_score(
                turns,
                existing_summary
            )
        )

        strengths = (
            self._collect_strengths(
                turns
            )
        )

        improvements = (
            self._collect_improvements(
                turns
            )
        )

        if not strengths:

            strengths = [
                (
                    "The trainee completed "
                    "the customer interaction."
                )
            ]

        if not improvements:

            improvements = [
                (
                    "Continue acknowledging "
                    "the customer's concern clearly."
                ),
                (
                    "Provide specific and actionable "
                    "next steps in every response."
                )
            ]

        if resolution_score >= 80:

            outcome = "Likely Resolved"

        elif resolution_score >= 60:

            outcome = "Partially Resolved"

        else:

            outcome = "Needs Improvement"

        total_turns = len(
            turns
        )

        interaction_summary = (
            f"The session contained "
            f"{total_turns} support turns for "
            f"the {session.get('scenario', 'support')} "
            f"scenario. The trainee interacted with "
            f"the customer and received evaluation "
            f"and coaching feedback throughout "
            f"the conversation."
        )

        return {

            "source":
                "fallback",

            "interaction_summary":
                interaction_summary,

            "sentiment_journey":
                sentiment_journey,

            "resolution_quality_score":
                resolution_score,

            "customer_outcome":
                outcome,

            "key_strengths":
                strengths[:5],

            "coaching_recommendations":
                improvements[:5],

            "knowledge_gaps":
                [],

            "final_observation": (
                "The final analysis was generated "
                "using the stored session metrics."
            )

        }


    def generate_summary(
        self,
        session,
        existing_summary=None
    ):
        """
        Generates the complete
        post-interaction analysis.
        """

        if not session:

            raise ValueError(
                "Session data is required"
            )

        existing_summary = (
            existing_summary or {}
        )

        turns = session.get(
            "turns",
            []
        )

        if not isinstance(
            turns,
            list
        ):

            turns = []

        if not turns:

            return {

                "source":
                    "fallback",

                "interaction_summary":
                    (
                        "No completed conversation "
                        "turns are available."
                    ),

                "sentiment_journey":
                    [],

                "resolution_quality_score":
                    0,

                "customer_outcome":
                    "Not Evaluated",

                "key_strengths":
                    [],

                "coaching_recommendations":
                    [
                        (
                            "Complete at least one "
                            "conversation turn to "
                            "receive coaching analysis."
                        )
                    ],

                "knowledge_gaps":
                    [],

                "final_observation":
                    (
                        "Insufficient interaction "
                        "data is available."
                    )

            }

        sentiment_journey = (
            self._get_sentiment_journey(
                turns
            )
        )

        base_resolution_score = (
            self._calculate_resolution_score(
                turns,
                existing_summary
            )
        )

        if not self.client:

            return self._fallback_summary(
                session,
                existing_summary
            )

        session_context = {

            "session_id":
                session.get(
                    "session_id"
                ),

            "interaction_mode":
                session.get(
                    "interaction_mode"
                ),

            "product":
                session.get(
                    "product"
                ),

            "scenario":
                session.get(
                    "scenario"
                ),

            "customer_persona":
                session.get(
                    "customer_persona"
                ),

            "difficulty":
                session.get(
                    "difficulty"
                ),

            "language":
                session.get(
                    "language"
                ),

            "total_turns":
                len(turns),

            "existing_summary":
                existing_summary,

            "sentiment_journey":
                sentiment_journey,

            "conversation_turns":
                turns

        }

        prompt = f"""
Completed Customer Support Session:

{json.dumps(
    session_context,
    ensure_ascii=False,
    indent=2
)}

Analyze the complete interaction.

Return only this JSON structure:

{{
  "source": "gemini",
  "interaction_summary":
      "Short summary of what happened during the session",

  "sentiment_journey": [
    {{
      "turn": 1,
      "sentiment": "Negative",
      "frustration": "High",
      "observation":
          "Short explanation of the customer's emotional state"
    }}
  ],

  "resolution_quality_score": 0,

  "customer_outcome":
      "Resolved, Partially Resolved, or Needs Escalation",

  "key_strengths": [
      "Specific trainee strength"
  ],

  "coaching_recommendations": [
      "Specific personalized recommendation"
  ],

  "knowledge_gaps": [
      "Any knowledge or policy gap visible in the conversation"
  ],

  "final_observation":
      "Short overall coaching observation"
}}

Rules:

- Resolution quality score must be from 0 to 100.
- Analyze the whole conversation, not only the last turn.
- Track how sentiment changed from turn to turn.
- Recommendations must be personalized to the trainee.
- Use existing evaluation scores as evidence.
- Use the supplied knowledge information when relevant.
- Do not invent company policy.
- Keep the output concise.
- Return valid JSON only.

Current calculated resolution score:
{base_resolution_score}
"""

        try:

            interaction = (
                self.client.interactions.create(
                    model=
                        "gemini-3.1-flash-lite",
                    system_instruction=
                        SYSTEM_PROMPT,
                    input=
                        prompt
                )
            )

            output_text = (
                self._clean_json_output(
                    interaction.output_text
                )
            )

            result = json.loads(
                output_text
            )

            if not isinstance(
                result,
                dict
            ):

                raise ValueError(
                    "Post-interaction response "
                    "is not a JSON object"
                )

            result.setdefault(
                "source",
                "gemini"
            )

            result.setdefault(
                "interaction_summary",
                ""
            )

            result.setdefault(
                "sentiment_journey",
                sentiment_journey
            )

            result.setdefault(
                "resolution_quality_score",
                base_resolution_score
            )

            result.setdefault(
                "customer_outcome",
                existing_summary.get(
                    "customer_outcome",
                    "Not Evaluated"
                )
            )

            result.setdefault(
                "key_strengths",
                []
            )

            result.setdefault(
                "coaching_recommendations",
                []
            )

            result.setdefault(
                "knowledge_gaps",
                []
            )

            result.setdefault(
                "final_observation",
                ""
            )

            result[
                "resolution_quality_score"
            ] = self._normalize_score(
                result.get(
                    "resolution_quality_score",
                    base_resolution_score
                )
            )

            if not isinstance(
                result.get(
                    "sentiment_journey"
                ),
                list
            ):

                result[
                    "sentiment_journey"
                ] = sentiment_journey

            if not isinstance(
                result.get(
                    "key_strengths"
                ),
                list
            ):

                result[
                    "key_strengths"
                ] = []

            if not isinstance(
                result.get(
                    "coaching_recommendations"
                ),
                list
            ):

                result[
                    "coaching_recommendations"
                ] = []

            if not isinstance(
                result.get(
                    "knowledge_gaps"
                ),
                list
            ):

                result[
                    "knowledge_gaps"
                ] = []

            return result

        except Exception as error:

            print(
                "POST INTERACTION SUMMARY ERROR =",
                error
            )

            return self._fallback_summary(
                session,
                existing_summary
            )