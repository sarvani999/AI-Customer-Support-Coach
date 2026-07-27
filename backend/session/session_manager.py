"""
Session Manager

Stores customer support simulation sessions,
conversation turns, scores, and report data.
"""

from datetime import datetime
from uuid import uuid4


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(
        self,
        product,
        scenario,
        customer_persona,
        difficulty="Medium",
        language="English"
    ):
        """
        Creates a new simulation session.
        """

        session_id = str(uuid4())

        session_data = {
            "session_id": session_id,
            "product": product,
            "scenario": scenario,
            "customer_persona": customer_persona,
            "difficulty": difficulty,
            "language": language,
            "status": "Active",
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "turns": [],
            "summary": {}
        }

        self.sessions[session_id] = session_data

        return session_data

    def get_session(self, session_id):
        """
        Returns a session using its session ID.
        """

        return self.sessions.get(session_id)

    def add_turn(
        self,
        session_id,
        customer_message,
        agent_reply,
        customer_analysis,
        evaluation,
        knowledge=None
    ):
        """
        Adds one conversation turn to the session.
        """

        session = self.get_session(session_id)

        if not session:
            raise ValueError("Session not found")

        if session["status"] != "Active":
            raise ValueError("Cannot add turns to a completed session")

        turn_number = len(session["turns"]) + 1

        turn = {
            "turn_number": turn_number,
            "customer_message": customer_message,
            "agent_reply": agent_reply,
            "customer_analysis": customer_analysis or {},
            "evaluation": evaluation or {},
            "knowledge": knowledge or {},
            "timestamp": datetime.now().isoformat()
        }

        session["turns"].append(turn)

        return turn

    def get_turns(self, session_id):
        """
        Returns all conversation turns from a session.
        """

        session = self.get_session(session_id)

        if not session:
            return []

        return session["turns"]

    def calculate_summary(self, session_id):
        """
        Calculates overall session scores and analytics.
        """

        session = self.get_session(session_id)

        if not session:
            raise ValueError("Session not found")

        turns = session["turns"]

        if not turns:
            summary = {
                "overall_score": 0,
                "average_empathy": 0,
                "average_clarity": 0,
                "average_tone": 0,
                "average_policy_accuracy": 0,
                "average_resolution": 0,
                "average_professionalism": 0,
                "average_resolution_probability": 0,
                "total_turns": 0,
                "highest_escalation_risk": "Low",
                "conversation_health": "No Data",
                "customer_outcome": "Not Evaluated",
                "grade": "N/A"
            }

            session["summary"] = summary
            return summary

        score_fields = {
            "overall_score": "overall_score",
            "average_empathy": "empathy_score",
            "average_clarity": "clarity_score",
            "average_tone": "tone_score",
            "average_policy_accuracy": "policy_accuracy",
            "average_resolution": "resolution_score",
            "average_professionalism": "professionalism_score",
            "average_resolution_probability": "resolution_probability"
        }

        summary = {}

        for summary_key, evaluation_key in score_fields.items():

            values = [
                turn["evaluation"].get(evaluation_key, 0)
                for turn in turns
            ]

            summary[summary_key] = round(
                sum(values) / len(values)
            )

        summary["total_turns"] = len(turns)

        risks = [
            turn["evaluation"].get("escalation_risk", "Low")
            for turn in turns
        ]

        if "High" in risks:
            summary["highest_escalation_risk"] = "High"
        elif "Medium" in risks:
            summary["highest_escalation_risk"] = "Medium"
        else:
            summary["highest_escalation_risk"] = "Low"

        final_evaluation = turns[-1]["evaluation"]

        summary["conversation_health"] = final_evaluation.get(
            "conversation_health",
            "Unknown"
        )

        resolution_probability = summary[
            "average_resolution_probability"
        ]

        if resolution_probability >= 80:
            summary["customer_outcome"] = "Likely Resolved"
        elif resolution_probability >= 60:
            summary["customer_outcome"] = "Partially Resolved"
        else:
            summary["customer_outcome"] = "Needs Escalation"

        overall_score = summary["overall_score"]

        if overall_score >= 90:
            summary["grade"] = "A+"
        elif overall_score >= 80:
            summary["grade"] = "A"
        elif overall_score >= 70:
            summary["grade"] = "B"
        elif overall_score >= 60:
            summary["grade"] = "C"
        elif overall_score >= 50:
            summary["grade"] = "D"
        else:
            summary["grade"] = "Needs Improvement"

        session["summary"] = summary

        return summary

    def end_session(self, session_id):
        """
        Completes a session and generates its final summary.
        """

        session = self.get_session(session_id)

        if not session:
            raise ValueError("Session not found")

        summary = self.calculate_summary(session_id)

        session["status"] = "Completed"
        session["ended_at"] = datetime.now().isoformat()

        return {
            "session": session,
            "summary": summary
        }

    def get_report_data(self, session_id):
        """
        Returns complete data needed for the report page.
        """

        session = self.get_session(session_id)

        if not session:
            raise ValueError("Session not found")

        if not session.get("summary"):
            self.calculate_summary(session_id)

        turns = session["turns"]

        report_data = {
            "session": session,
            "summary": session["summary"],
            "charts": {
                "turn_labels": [
                    f"Turn {turn['turn_number']}"
                    for turn in turns
                ],
                "overall_scores": [
                    turn["evaluation"].get("overall_score", 0)
                    for turn in turns
                ],
                "empathy_scores": [
                    turn["evaluation"].get("empathy_score", 0)
                    for turn in turns
                ],
                "clarity_scores": [
                    turn["evaluation"].get("clarity_score", 0)
                    for turn in turns
                ],
                "tone_scores": [
                    turn["evaluation"].get("tone_score", 0)
                    for turn in turns
                ],
                "policy_scores": [
                    turn["evaluation"].get("policy_accuracy", 0)
                    for turn in turns
                ],
                "resolution_scores": [
                    turn["evaluation"].get("resolution_score", 0)
                    for turn in turns
                ],
                "professionalism_scores": [
                    turn["evaluation"].get(
                        "professionalism_score",
                        0
                    )
                    for turn in turns
                ],
                "resolution_probabilities": [
                    turn["evaluation"].get(
                        "resolution_probability",
                        0
                    )
                    for turn in turns
                ],
                "frustration_levels": [
                    self._convert_frustration_to_score(
                        turn["customer_analysis"].get(
                            "frustration_level",
                            "Medium"
                        )
                    )
                    for turn in turns
                ]
            },
            "strengths": self._collect_feedback(
                turns,
                "strengths"
            ),
            "improvements": self._collect_feedback(
                turns,
                "improvements"
            )
        }

        return report_data

    def _convert_frustration_to_score(self, level):
        """
        Converts frustration labels to numerical chart values.
        """

        values = {
            "Low": 25,
            "Medium": 60,
            "High": 90
        }

        return values.get(level, 60)

    def _collect_feedback(self, turns, key):
        """
        Collects unique strengths or improvements.
        """

        feedback = []

        for turn in turns:

            items = turn["evaluation"].get(key, [])

            for item in items:

                if item not in feedback:
                    feedback.append(item)

        return feedback

    def list_sessions(self):
        """
        Returns all sessions.
        """

        return list(self.sessions.values())


session_manager = SessionManager()