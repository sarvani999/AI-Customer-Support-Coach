class EscalationAgent:
    """
    Monitors escalation risk for every customer turn.
    """

    def check_risk(self, analysis, customer_message):

        message = customer_message.lower()

        risk_score = 0
        reasons = []

        frustration = analysis.get(
            "frustration_level",
            ""
        ).lower()

        sentiment = analysis.get(
            "sentiment",
            ""
        ).lower()

        if frustration == "high":
            risk_score += 40
            reasons.append(
                "Customer frustration is high."
            )

        if sentiment == "negative":
            risk_score += 25
            reasons.append(
                "Customer sentiment is negative."
            )

        keywords = [
            "refund",
            "manager",
            "cancel",
            "complaint",
            "legal",
            "angry",
            "worst"
        ]

        for word in keywords:

            if word in message:
                risk_score += 10
                reasons.append(
                    f"Detected keyword: {word}"
                )

        if risk_score >= 70:
            level = "High"

        elif risk_score >= 40:
            level = "Medium"

        else:
            level = "Low"

        return {

            "risk_score": risk_score,

            "risk_level": level,

            "reasoning": reasons

        }