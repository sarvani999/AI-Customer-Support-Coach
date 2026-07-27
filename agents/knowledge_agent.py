SYSTEM_PROMPT = """
You are an AI Knowledge Recommendation Agent for a Customer Support Coaching Assistant.

Role:
- Recommend the most relevant knowledge base article based on the customer's issue.

Instructions:
- Analyze the customer's message carefully.
- Identify the customer's issue.
- Retrieve the most relevant knowledge article.
- Return only the most appropriate knowledge recommendation.
- If no exact match is found, recommend general support guidance.
"""


class KnowledgeRecommendationAgent:

    def __init__(self):

        self.system_prompt = SYSTEM_PROMPT

        self.knowledge_base = {

            "return": {

                "title": "Amazon Return Policy",

                "content": "Customers can return eligible products within the return window. Check order details and initiate return request."

            },

            "refund": {

                "title": "Refund Guidelines",

                "content": "Refunds are processed after product verification. Amount will be credited to the original payment method."

            },

            "delivery": {

                "title": "Delivery Support",

                "content": "Check delivery status using order tracking. Contact support if delivery is delayed."

            }

        }

    def retrieve_knowledge(self, message):

        # System prompt available for future LLM integration
        # print(self.system_prompt)

        text = message.lower()

        if "return" in text:

            return self.knowledge_base["return"]

        elif "refund" in text:

            return self.knowledge_base["refund"]

        elif "delivery" in text or "late" in text:

            return self.knowledge_base["delivery"]

        else:

            return {

                "title": "General Support",

                "content": "Please collect more details from the customer and provide appropriate assistance."

            }