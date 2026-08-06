import re

try:
    from agents.knowledge_storage import (
        knowledge_storage
    )

except ImportError:
    try:
        from knowledge_storage import (
            knowledge_storage
        )

    except ImportError:
        knowledge_storage = None


SYSTEM_PROMPT = """
You are an AI Knowledge Recommendation Agent
for a Customer Support Coaching Assistant.

Your responsibility is to retrieve the most relevant
knowledge-base guidance for the customer's issue.

Rules:
- Prefer uploaded knowledge documents.
- Match the selected product when possible.
- Match the selected scenario when possible.
- Analyze the customer message carefully.
- Return only knowledge supported by stored documents.
- Do not invent company policy.
- If no uploaded document matches, return safe fallback guidance.
"""


class KnowledgeRecommendationAgent:
    """
    Retrieves relevant support knowledge
    from uploaded documents.

    If no uploaded document matches,
    safe built-in guidance is returned.
    """

    def __init__(self):

        self.system_prompt = SYSTEM_PROMPT

        self.default_knowledge = {

            "return request": {
                "title":
                    "Return Support Guidance",

                "scenario":
                    "Return Request",

                "content": (
                    "Verify whether the item is eligible "
                    "for return and guide the customer "
                    "through the available return process."
                )
            },

            "refund delay": {
                "title":
                    "Refund Delay Guidance",

                "scenario":
                    "Refund Delay",

                "content": (
                    "Verify whether the returned item "
                    "has been received and processed. "
                    "Check the refund status and provide "
                    "a clear next step without promising "
                    "an unsupported timeline."
                )
            },

            "refund request": {
                "title":
                    "Refund Request Guidance",

                "scenario":
                    "Refund Request",

                "content": (
                    "Check whether the refund request "
                    "meets the required conditions and "
                    "confirm the next supported action."
                )
            },

            "wrong product": {
                "title":
                    "Wrong Product Guidance",

                "scenario":
                    "Wrong Product",

                "content": (
                    "Confirm the ordered product and "
                    "the item received. Guide the customer "
                    "through the available return or "
                    "replacement process."
                )
            },

            "damaged product": {
                "title":
                    "Damaged Product Guidance",

                "scenario":
                    "Damaged Product",

                "content": (
                    "Confirm the product condition and "
                    "collect the required order details. "
                    "Guide the customer through the "
                    "supported replacement or return steps."
                )
            },

            "late delivery": {
                "title":
                    "Late Delivery Guidance",

                "scenario":
                    "Late Delivery",

                "content": (
                    "Check the latest tracking status "
                    "and expected delivery information. "
                    "Provide a clear next action when "
                    "the delivery is delayed."
                )
            },

            "missing item": {
                "title":
                    "Missing Item Guidance",

                "scenario":
                    "Missing Item",

                "content": (
                    "Confirm the ordered and delivered "
                    "items. Check whether the order was "
                    "split into multiple packages before "
                    "starting a missing-item resolution."
                )
            },

            "order cancellation": {
                "title":
                    "Order Cancellation Guidance",

                "scenario":
                    "Order Cancellation",

                "content": (
                    "Check the current order status before "
                    "confirming whether cancellation is "
                    "available."
                )
            },

            "payment issue": {
                "title":
                    "Payment Issue Guidance",

                "scenario":
                    "Payment Issue",

                "content": (
                    "Verify the payment and order status. "
                    "Check for duplicate charges, failed "
                    "transactions, or pending confirmation."
                )
            },

            "exchange request": {
                "title":
                    "Exchange Request Guidance",

                "scenario":
                    "Exchange Request",

                "content": (
                    "Confirm the requested size, variant, "
                    "or replacement and guide the customer "
                    "through the supported exchange process."
                )
            }
        }


    def _normalize_text(
        self,
        value
    ):
        """
        Converts text into a normalized
        form for matching.
        """

        text = str(
            value or ""
        ).strip().lower()

        text = re.sub(
            r"[^a-z0-9\u0C00-\u0C7F\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    def _detect_scenario(
        self,
        customer_message
    ):
        """
        Detects the most likely scenario
        from the customer message.
        """

        text = self._normalize_text(
            customer_message
        )

        scenario_keywords = {

            "refund delay": [
                "refund not received",
                "refund pending",
                "refund delayed",
                "still no refund",
                "where is my refund",
                "money not credited",
                "amount not credited",
                "refund status"
            ],

            "refund request": [
                "want a refund",
                "need a refund",
                "request refund",
                "refund this"
            ],

            "return request": [
                "want to return",
                "return item",
                "return product",
                "return order"
            ],

            "wrong product": [
                "wrong product",
                "wrong item",
                "different item",
                "incorrect product"
            ],

            "damaged product": [
                "damaged",
                "broken",
                "cracked",
                "defective"
            ],

            "late delivery": [
                "late delivery",
                "not delivered",
                "delivery delayed",
                "order delayed",
                "tracking not updated"
            ],

            "missing item": [
                "missing item",
                "item missing",
                "not inside package",
                "incomplete order"
            ],

            "order cancellation": [
                "cancel order",
                "cancel my order",
                "order cancellation"
            ],

            "payment issue": [
                "payment failed",
                "charged twice",
                "double charged",
                "money deducted",
                "payment pending"
            ],

            "exchange request": [
                "exchange item",
                "exchange product",
                "different size",
                "different variant"
            ]
        }

        for scenario_name, keywords in (
            scenario_keywords.items()
        ):

            for keyword in keywords:

                if keyword in text:

                    return scenario_name

        if "refund" in text:
            return "refund request"

        if "return" in text:
            return "return request"

        if (
            "delivery" in text or
            "tracking" in text
        ):
            return "late delivery"

        if "payment" in text:
            return "payment issue"

        return "general support"


    def _normalize_scenario(
        self,
        scenario
    ):
        """
        Converts selected scenario names
        into storage-compatible keys.
        """

        scenario_text = self._normalize_text(
            scenario
        )

        scenario_aliases = {

            "refund delayed":
                "refund delay",

            "delayed refund":
                "refund delay",

            "refund status":
                "refund delay",

            "return":
                "return request",

            "refund":
                "refund request",

            "wrong item":
                "wrong product",

            "damaged item":
                "damaged product",

            "delivery delay":
                "late delivery",

            "cancel order":
                "order cancellation",

            "exchange":
                "exchange request"
        }

        return scenario_aliases.get(
            scenario_text,
            scenario_text
        )


    def _search_uploaded_knowledge(
        self,
        product,
        scenario,
        customer_message
    ):
        """
        Searches uploaded knowledge documents.
        """

        if knowledge_storage is None:

            return None

        try:

            results = knowledge_storage.search(
                query=customer_message,
                product=product,
                scenario=scenario,
                top_k=3
            )

            if not results:

                return None

            if isinstance(
                results,
                list
            ):

                best_result = results[0]

            elif isinstance(
                results,
                dict
            ):

                best_result = results

            else:

                return None

            content = str(
                best_result.get(
                    "content",
                    best_result.get(
                        "text",
                        ""
                    )
                )
            ).strip()

            if not content:

                return None

            return {
                "title":
                    best_result.get(
                        "title",
                        "Uploaded Knowledge"
                    ),

                "product":
                    best_result.get(
                        "product",
                        product
                    ),

                "scenario":
                    best_result.get(
                        "scenario",
                        scenario
                    ),

                "content":
                    content,

                "source":
                    best_result.get(
                        "file_name",
                        best_result.get(
                            "source",
                            "Uploaded document"
                        )
                    ),

                "page_number":
                    best_result.get(
                        "page_number"
                    ),

                "confidence":
                    best_result.get(
                        "confidence",
                        best_result.get(
                            "score",
                            0
                        )
                    ),

                "match_type":
                    "uploaded_knowledge"
            }

        except Exception as error:

            print(
                "UPLOADED KNOWLEDGE SEARCH ERROR =",
                error
            )

            return None


    def _get_default_knowledge(
        self,
        product,
        scenario
    ):
        """
        Returns safe fallback guidance when no
        uploaded document matches.
        """

        scenario_key = self._normalize_scenario(
            scenario
        )

        guidance = self.default_knowledge.get(
            scenario_key
        )

        if not guidance:

            guidance = {
                "title":
                    "General Support Guidance",

                "scenario":
                    scenario
                    or "General Support",

                "content": (
                    "Collect the relevant customer and "
                    "order details, verify the issue, and "
                    "provide a clear next step. Do not "
                    "invent policy or promise an outcome "
                    "before verification."
                )
            }

        return {
            "title":
                guidance["title"],

            "product":
                product or "General",

            "scenario":
                guidance["scenario"],

            "content":
                guidance["content"],

            "source":
                "Built-in fallback guidance",

            "page_number":
                None,

            "confidence":
                0,

            "match_type":
                "fallback",

            "notice": (
                "No matching uploaded knowledge "
                "document was found."
            )
        }


    def retrieve_knowledge(
        self,
        product,
        message=None,
        scenario=None
    ):
        """
        Retrieves the most relevant knowledge.

        Supports:

        retrieve_knowledge(message)

        retrieve_knowledge(product, message)

        retrieve_knowledge(
            product,
            message,
            scenario
        )
        """

        if message is None:

            message = product

            product = "General"

        product_name = str(
            product or "General"
        ).strip()

        customer_message = str(
            message or ""
        ).strip()

        if scenario:

            detected_scenario = (
                self._normalize_scenario(
                    scenario
                )
            )

        else:

            detected_scenario = (
                self._detect_scenario(
                    customer_message
                )
            )

        if not customer_message:

            return self._get_default_knowledge(
                product_name,
                detected_scenario
            )

        uploaded_result = (
            self._search_uploaded_knowledge(
                product=product_name,
                scenario=detected_scenario,
                customer_message=
                    customer_message
            )
        )

        if uploaded_result:

            return uploaded_result

        return self._get_default_knowledge(
            product_name,
            detected_scenario
        )