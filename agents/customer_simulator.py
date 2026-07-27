import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


SYSTEM_PROMPT = """
You are an AI Customer Simulator for a Customer Support Coaching Assistant.

Role:
- Act as a realistic customer interacting with a customer support agent.
- Simulate customer conversations based on the selected product, scenario,
  customer persona, and language.

Instructions:
- Always behave like the customer, never as the support agent.
- Follow the selected customer persona: Frustrated, Angry, Calm, or Confused.
- Keep responses short, natural, and conversational.
- Stay focused on the current support issue.
- Do not provide solutions; only express the customer's concerns.
- Always reply only in the selected language.
- Do not switch to English unless English is the selected language.
"""


class CustomerSimulatorAgent:

    def __init__(self):

        self.system_prompt = SYSTEM_PROMPT
        self.turn = 0

        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:

            self.client = genai.Client(
                api_key=api_key
            )

        else:

            self.client = None


    def _fallback_response(
        self,
        product,
        scenario,
        persona,
        language
    ):

        selected_language = str(
            language or "English"
        ).strip().lower()

        scenario_name = str(
            scenario or ""
        ).strip().lower()

        persona_name = str(
            persona or ""
        ).strip().lower()


        if selected_language == "telugu":

            return self._telugu_fallback(
                product,
                scenario_name,
                persona_name
            )


        return self._english_fallback(
            product,
            scenario_name,
            persona_name
        )


    def _english_fallback(
        self,
        product,
        scenario,
        persona
    ):

        if scenario == "return request":

            if persona == "frustrated":

                messages = [

                    (
                        f"I am really disappointed with my "
                        f"{product} order. I want to return it."
                    ),

                    (
                        "I already tried contacting support, "
                        "but my issue is still not resolved."
                    ),

                    (
                        "This is taking too long. "
                        "I need a proper solution immediately."
                    )

                ]

            elif persona == "angry":

                messages = [

                    (
                        f"My {product} order is unacceptable. "
                        "I want to return it immediately."
                    ),

                    "I am tired of waiting for a proper response.",

                    (
                        "This is the worst shopping experience "
                        "I have had."
                    )

                ]

            else:

                messages = [

                    f"I would like to return my {product} order.",

                    "Can you please help me with the return process?",

                    "Thank you for helping me."

                ]

        elif scenario == "late delivery":

            messages = [

                f"My {product} order is delayed.",

                "The delivery date has already passed.",

                "Can you please check the status?"

            ]

        else:

            messages = [

                f"I have an issue with my {product}.",

                "Can you help me resolve this problem?",

                "I am waiting for an update."

            ]


        if self.turn <= len(messages):

            return messages[self.turn - 1]


        return "Thank you for your support."


    def _telugu_fallback(
        self,
        product,
        scenario,
        persona
    ):

        if scenario == "return request":

            if persona == "frustrated":

                messages = [

                    (
                        f"నేను కొనుగోలు చేసిన {product} ఉత్పత్తితో "
                        "చాలా నిరాశ చెందాను. దాన్ని తిరిగి ఇవ్వాలనుకుంటున్నాను."
                    ),

                    (
                        "నేను ఇప్పటికే సపోర్ట్‌ను సంప్రదించాను, "
                        "కానీ నా సమస్య ఇంకా పరిష్కారం కాలేదు."
                    ),

                    (
                        "ఇది చాలా సమయం తీసుకుంటోంది. "
                        "నాకు వెంటనే సరైన పరిష్కారం కావాలి."
                    )

                ]

            elif persona == "angry":

                messages = [

                    (
                        f"నేను కొనుగోలు చేసిన {product} ఉత్పత్తి "
                        "అసలు సరైనది కాదు. వెంటనే రిటర్న్ చేయాలి."
                    ),

                    (
                        "సరైన సమాధానం కోసం ఎదురుచూసి "
                        "నేను విసిగిపోయాను."
                    ),

                    (
                        "ఇది నాకు ఎదురైన అత్యంత చెత్త "
                        "షాపింగ్ అనుభవం."
                    )

                ]

            else:

                messages = [

                    (
                        f"నేను కొనుగోలు చేసిన {product} ఉత్పత్తిని "
                        "రిటర్న్ చేయాలనుకుంటున్నాను."
                    ),

                    (
                        "రిటర్న్ ప్రక్రియలో నాకు "
                        "సహాయం చేయగలరా?"
                    ),

                    "సహాయం చేసినందుకు ధన్యవాదాలు."

                ]

        elif scenario == "late delivery":

            messages = [

                f"నా {product} ఆర్డర్ ఆలస్యమైంది.",

                "డెలివరీ తేదీ ఇప్పటికే దాటిపోయింది.",

                "దయచేసి ఆర్డర్ స్థితిని చెక్ చేయగలరా?"

            ]

        else:

            messages = [

                f"నా {product} ఉత్పత్తితో ఒక సమస్య ఉంది.",

                (
                    "ఈ సమస్యను పరిష్కరించడానికి "
                    "నాకు సహాయం చేయగలరా?"
                ),

                "నేను అప్డేట్ కోసం ఎదురుచూస్తున్నాను."

            ]


        if self.turn <= len(messages):

            return messages[self.turn - 1]


        return "మీ సహాయానికి ధన్యవాదాలు."


    def generate_message(
        self,
        product,
        scenario,
        persona,
        language="English"
    ):

        self.turn += 1

        selected_language = str(
            language or "English"
        ).strip()


        if self.client:

            try:

                prompt = f"""
Product: {product}
Scenario: {scenario}
Customer Persona: {persona}
Selected Language: {selected_language}
Conversation Turn: {self.turn}

Generate ONLY the customer's next message.

Rules:
- Behave only as the customer.
- Do not answer as the support agent.
- Keep the message between 1 and 2 sentences.
- Make every turn feel like a continuation of the conversation.
- Reply only in {selected_language}.
- Do not translate the response into English.
- Do not mix multiple languages.
- If the selected language is Telugu, use Telugu script.
"""

                interaction = self.client.interactions.create(

                    model="gemini-3.1-flash-lite",

                    system_instruction=self.system_prompt,

                    input=prompt

                )


                message = interaction.output_text.strip()


                if message:

                    return message


            except Exception as error:

                print(
                    "Gemini Error:",
                    error
                )


        return self._fallback_response(

            product=product,

            scenario=scenario,

            persona=persona,

            language=selected_language

        )