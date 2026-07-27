SYSTEM_PROMPT = """
You are an AI Intent and Sentiment Analysis Agent for a Customer Support Coaching Assistant.

Role:
- Analyze the customer's message.
- Identify the customer's intent.
- Detect the customer's sentiment.
- Estimate the customer's frustration level.

Instructions:
- Read the customer's message carefully.
- Classify the intent accurately.
- Determine whether the sentiment is Positive, Neutral, or Negative.
- Estimate the frustration level as Low, Medium, or High.
- Return only structured analysis results.
"""


class IntentSentimentAgent:

    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

    def analyze(self, message):

        # System prompt available for future LLM integration
        # print(self.system_prompt)

        text = message.lower()

        # Intent detection

        if "return" in text or "refund" in text:

            intent = "Return Request"

        elif "delivery" in text or "late" in text:

            intent = "Delivery Issue"

        elif "cancel" in text:

            intent = "Cancellation"

        else:

            intent = "General Support"

        # Sentiment detection

        if any(word in text for word in [
            "angry",
            "disappointed",
            "frustrated",
            "not resolved",
            "immediately"
        ]):

            sentiment = "Negative"
            frustration = "High"

        elif any(word in text for word in [
            "thank",
            "great",
            "happy"
        ]):

            sentiment = "Positive"
            frustration = "Low"

        else:

            sentiment = "Neutral"
            frustration = "Medium"

        return {

            "intent": intent,

            "sentiment": sentiment,

            "frustration_level": frustration

        }