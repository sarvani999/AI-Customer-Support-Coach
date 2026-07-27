"""
Response Evaluator Agent

This module evaluates the customer support agent's reply
and generates coaching scores and recommendations.
"""


class ResponseEvaluator:

    def __init__(self):
        self.empathy_phrases = [
            "i understand",
            "i completely understand",
            "i'm sorry",
            "i am sorry",
            "sorry to hear",
            "apologize",
            "i understand your frustration",
            "i understand your concern"
        ]

        self.professional_phrases = [
            "please",
            "thank you",
            "kindly",
            "allow me",
            "let me help",
            "i will assist",
            "i can help",
            "happy to help"
        ]

        self.resolution_phrases = [
            "refund",
            "replacement",
            "return",
            "cancel",
            "track",
            "resolve",
            "process",
            "check",
            "assist",
            "help you",
            "order id",
            "order number"
        ]

        self.negative_phrases = [
            "calm down",
            "not my problem",
            "you are wrong",
            "wait",
            "can't help",
            "cannot help",
            "stop complaining",
            "that's your fault"
        ]

        self.policy_phrases = [
            "return policy",
            "refund policy",
            "refund timeline",
            "business days",
            "eligible",
            "replacement",
            "return window",
            "terms and conditions"
        ]

    def _limit_score(self, score):
        """
        Keeps score between 0 and 100.
        """

        return max(0, min(100, int(score)))

    def _contains_phrase(self, text, phrases):
        """
        Checks whether the text contains any phrase
        from the given phrase list.
        """

        return any(phrase in text for phrase in phrases)

    def _calculate_empathy_score(self, agent_reply, customer_message):
        score = 45

        if self._contains_phrase(agent_reply, self.empathy_phrases):
            score += 35

        if any(word in customer_message for word in [
            "angry",
            "frustrated",
            "disappointed",
            "upset",
            "damaged",
            "late"
        ]):
            if self._contains_phrase(agent_reply, self.empathy_phrases):
                score += 15
            else:
                score -= 15

        if self._contains_phrase(agent_reply, self.negative_phrases):
            score -= 35

        return self._limit_score(score)

    def _calculate_tone_score(self, agent_reply):
        score = 60

        if self._contains_phrase(agent_reply, self.professional_phrases):
            score += 20

        if self._contains_phrase(agent_reply, self.empathy_phrases):
            score += 10

        if self._contains_phrase(agent_reply, self.negative_phrases):
            score -= 40

        if agent_reply.isupper() and len(agent_reply) > 5:
            score -= 25

        if agent_reply.count("!") > 2:
            score -= 10

        return self._limit_score(score)

    def _calculate_clarity_score(self, agent_reply):
        score = 55

        word_count = len(agent_reply.split())
        sentence_count = (
            agent_reply.count(".")
            + agent_reply.count("?")
            + agent_reply.count("!")
        )

        if 12 <= word_count <= 80:
            score += 20

        elif word_count < 5:
            score -= 25

        elif word_count > 120:
            score -= 15

        if sentence_count >= 1:
            score += 10

        if any(word in agent_reply for word in [
            "first",
            "next",
            "then",
            "please share",
            "please provide"
        ]):
            score += 10

        return self._limit_score(score)

    def _calculate_policy_score(self, agent_reply):
        score = 50

        if self._contains_phrase(agent_reply, self.policy_phrases):
            score += 30

        if any(word in agent_reply for word in [
            "verify",
            "order id",
            "order number",
            "eligibility",
            "return window"
        ]):
            score += 15

        if any(word in agent_reply for word in [
            "guaranteed refund",
            "instant refund",
            "definitely refunded"
        ]):
            score -= 30

        return self._limit_score(score)

    def _calculate_resolution_score(self, agent_reply):
        score = 45

        if self._contains_phrase(agent_reply, self.resolution_phrases):
            score += 25

        if any(phrase in agent_reply for phrase in [
            "please share your order id",
            "please provide your order id",
            "let me check",
            "i can process",
            "i can assist",
            "here are the next steps"
        ]):
            score += 20

        if agent_reply.strip().endswith("?"):
            score += 5

        if self._contains_phrase(agent_reply, self.negative_phrases):
            score -= 35

        return self._limit_score(score)

    def _calculate_professionalism_score(self, agent_reply):
        score = 60

        if self._contains_phrase(agent_reply, self.professional_phrases):
            score += 20

        if self._contains_phrase(agent_reply, self.empathy_phrases):
            score += 10

        if agent_reply and agent_reply[0].isupper():
            score += 5

        if self._contains_phrase(agent_reply, self.negative_phrases):
            score -= 40

        return self._limit_score(score)

    def _get_escalation_risk(
        self,
        empathy_score,
        tone_score,
        resolution_score,
        customer_message
    ):
        risk_score = 0

        if empathy_score < 50:
            risk_score += 2

        if tone_score < 50:
            risk_score += 2

        if resolution_score < 50:
            risk_score += 2

        if any(word in customer_message for word in [
            "manager",
            "complaint",
            "legal",
            "consumer court",
            "angry",
            "frustrated",
            "immediately"
        ]):
            risk_score += 2

        if risk_score >= 6:
            return "High"

        if risk_score >= 3:
            return "Medium"

        return "Low"

    def _get_conversation_health(
        self,
        empathy_score,
        tone_score,
        resolution_score,
        escalation_risk
    ):
        average = (
            empathy_score
            + tone_score
            + resolution_score
        ) / 3

        if escalation_risk == "High":
            return "Escalating"

        if average >= 80:
            return "Excellent"

        if average >= 65:
            return "Stable"

        if average >= 50:
            return "Recovering"

        return "At Risk"

    def _get_resolution_probability(
        self,
        empathy_score,
        clarity_score,
        tone_score,
        policy_score,
        resolution_score
    ):
        probability = (
            empathy_score * 0.20
            + clarity_score * 0.15
            + tone_score * 0.15
            + policy_score * 0.20
            + resolution_score * 0.30
        )

        return self._limit_score(probability)

    def _generate_strengths(
        self,
        empathy_score,
        clarity_score,
        tone_score,
        policy_score,
        resolution_score,
        professionalism_score
    ):
        strengths = []

        if empathy_score >= 75:
            strengths.append("Acknowledged the customer's concern")

        if clarity_score >= 75:
            strengths.append("Provided a clear and understandable response")

        if tone_score >= 75:
            strengths.append("Maintained a polite and supportive tone")

        if policy_score >= 75:
            strengths.append("Included relevant policy information")

        if resolution_score >= 75:
            strengths.append("Provided useful resolution steps")

        if professionalism_score >= 75:
            strengths.append("Maintained professional communication")

        if not strengths:
            strengths.append("Responded to the customer's message")

        return strengths

    def _generate_improvements(
        self,
        empathy_score,
        clarity_score,
        tone_score,
        policy_score,
        resolution_score,
        professionalism_score
    ):
        improvements = []

        if empathy_score < 70:
            improvements.append(
                "Acknowledge the customer's feelings before giving a solution"
            )

        if clarity_score < 70:
            improvements.append(
                "Use shorter and clearer sentences"
            )

        if tone_score < 70:
            improvements.append(
                "Use a calmer and more supportive tone"
            )

        if policy_score < 70:
            improvements.append(
                "Mention the relevant return or refund policy"
            )

        if resolution_score < 70:
            improvements.append(
                "Provide a clear next step or ask for the order ID"
            )

        if professionalism_score < 70:
            improvements.append(
                "Use polite and professional language"
            )

        if not improvements:
            improvements.append(
                "Mention the expected resolution timeline for better clarity"
            )

        return improvements

    def evaluate(
        self,
        customer_message,
        agent_reply,
        knowledge=None
    ):
        """
        Evaluates the support agent's response.

        Parameters:
            customer_message: Customer's current message.
            agent_reply: Support agent's reply.
            knowledge: Optional knowledge base result.

        Returns:
            Dictionary containing scores and coaching feedback.
        """

        customer_text = str(customer_message).lower().strip()
        agent_text = str(agent_reply).lower().strip()

        if not agent_text:
            return {
                "overall_score": 0,
                "empathy_score": 0,
                "clarity_score": 0,
                "tone_score": 0,
                "policy_accuracy": 0,
                "resolution_score": 0,
                "professionalism_score": 0,
                "escalation_risk": "High",
                "conversation_health": "At Risk",
                "resolution_probability": 0,
                "strengths": [],
                "improvements": [
                    "The agent response cannot be empty"
                ]
            }

        empathy_score = self._calculate_empathy_score(
            agent_text,
            customer_text
        )

        clarity_score = self._calculate_clarity_score(
            agent_text
        )

        tone_score = self._calculate_tone_score(
            agent_text
        )

        policy_score = self._calculate_policy_score(
            agent_text
        )

        resolution_score = self._calculate_resolution_score(
            agent_text
        )

        professionalism_score = self._calculate_professionalism_score(
            agent_text
        )

        overall_score = self._limit_score(
            empathy_score * 0.20
            + clarity_score * 0.15
            + tone_score * 0.15
            + policy_score * 0.15
            + resolution_score * 0.20
            + professionalism_score * 0.15
        )

        escalation_risk = self._get_escalation_risk(
            empathy_score,
            tone_score,
            resolution_score,
            customer_text
        )

        conversation_health = self._get_conversation_health(
            empathy_score,
            tone_score,
            resolution_score,
            escalation_risk
        )

        resolution_probability = self._get_resolution_probability(
            empathy_score,
            clarity_score,
            tone_score,
            policy_score,
            resolution_score
        )

        strengths = self._generate_strengths(
            empathy_score,
            clarity_score,
            tone_score,
            policy_score,
            resolution_score,
            professionalism_score
        )

        improvements = self._generate_improvements(
            empathy_score,
            clarity_score,
            tone_score,
            policy_score,
            resolution_score,
            professionalism_score
        )

        return {
            "overall_score": overall_score,
            "empathy_score": empathy_score,
            "clarity_score": clarity_score,
            "tone_score": tone_score,
            "policy_accuracy": policy_score,
            "resolution_score": resolution_score,
            "professionalism_score": professionalism_score,
            "escalation_risk": escalation_risk,
            "conversation_health": conversation_health,
            "resolution_probability": resolution_probability,
            "strengths": strengths,
            "improvements": improvements
        }
if __name__ == "__main__":

    evaluator = ResponseEvaluator()

    customer_message = (
        "I am very frustrated because my Amazon order arrived damaged."
    )

    agent_reply = (
        "I am sorry to hear that. I understand your frustration. "
        "Please share your Order ID so I can check the return "
        "eligibility and help you with a replacement."
    )

    result = evaluator.evaluate(
        customer_message,
        agent_reply
    )

    from pprint import pprint
    pprint(result)