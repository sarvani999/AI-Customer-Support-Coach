"""
Session Manager

Stores customer support simulation sessions,
conversation turns, coaching data, escalation data,
scores, reports, post-interaction summaries,
and multi-session performance analytics.
"""

from collections import Counter
from datetime import datetime
from uuid import uuid4


class SessionManager:

    def __init__(self):
        self.sessions = {}


    def create_session(
        self,
        interaction_mode,
        product,
        scenario,
        customer_persona,
        difficulty="Medium",
        language="English"
    ):
        """
        Creates a new customer support
        coaching session.
        """

        session_id = str(uuid4())

        session_data = {

            "session_id":
                session_id,

            "interaction_mode":
                interaction_mode,

            "product":
                product,

            "scenario":
                scenario,

            "customer_persona":
                customer_persona,

            "difficulty":
                difficulty,

            "language":
                language,

            "status":
                "Active",

            "started_at":
                datetime.now().isoformat(),

            "ended_at":
                None,

            "turns":
                [],

            "summary":
                {},

            "post_interaction_summary":
                {}

        }

        self.sessions[
            session_id
        ] = session_data

        return session_data


    def get_session(
        self,
        session_id
    ):
        """
        Returns a session using
        its session ID.
        """

        return self.sessions.get(
            session_id
        )


    def add_turn(
        self,
        session_id,
        customer_message,
        agent_reply,
        customer_analysis,
        evaluation,
        knowledge=None,
        coaching=None,
        escalation=None
    ):
        """
        Stores one complete conversation turn.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            raise ValueError(
                "Session not found"
            )

        if (
            session.get("status")
            != "Active"
        ):
            raise ValueError(
                "Cannot add turns to a completed session"
            )

        turn_number = (
            len(
                session["turns"]
            )
            + 1
        )

        turn = {

            "turn_number":
                turn_number,

            "customer_message":
                customer_message,

            "agent_reply":
                agent_reply,

            "customer_analysis":
                customer_analysis or {},

            "knowledge":
                knowledge or {},

            "evaluation":
                evaluation or {},

            "coaching":
                coaching or {},

            "escalation":
                escalation or {},

            "timestamp":
                datetime.now().isoformat()

        }

        session[
            "turns"
        ].append(
            turn
        )

        return turn


    def get_turns(
        self,
        session_id
    ):
        """
        Returns all turns
        from a session.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            return []

        return session.get(
            "turns",
            []
        )


    def calculate_summary(
        self,
        session_id
    ):
        """
        Calculates numerical
        session summary.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            raise ValueError(
                "Session not found"
            )

        turns = session.get(
            "turns",
            []
        )

        if not turns:

            summary = {

                "overall_score":
                    0,

                "average_empathy":
                    0,

                "average_clarity":
                    0,

                "average_tone":
                    0,

                "average_policy_accuracy":
                    0,

                "average_resolution":
                    0,

                "average_professionalism":
                    0,

                "average_resolution_probability":
                    0,

                "total_turns":
                    0,

                "highest_escalation_risk":
                    "Low",

                "highest_escalation_score":
                    0,

                "conversation_health":
                    "No Data",

                "customer_outcome":
                    "Not Evaluated",

                "grade":
                    "N/A"

            }

            session[
                "summary"
            ] = summary

            return summary


        score_fields = {

            "overall_score":
                "overall_score",

            "average_empathy":
                "empathy_score",

            "average_clarity":
                "clarity_score",

            "average_tone":
                "tone_score",

            "average_policy_accuracy":
                "policy_accuracy",

            "average_resolution":
                "resolution_score",

            "average_professionalism":
                "professionalism_score",

            "average_resolution_probability":
                "resolution_probability"

        }


        summary = {}


        for (
            summary_key,
            evaluation_key
        ) in score_fields.items():

            values = []

            for turn in turns:

                evaluation = (
                    turn.get(
                        "evaluation",
                        {}
                    )
                    or {}
                )

                value = (
                    evaluation.get(
                        evaluation_key,
                        0
                    )
                )

                try:
                    values.append(
                        float(value)
                    )

                except (
                    TypeError,
                    ValueError
                ):
                    values.append(
                        0
                    )

            summary[
                summary_key
            ] = round(
                sum(values)
                /
                len(values)
            ) if values else 0


        summary[
            "total_turns"
        ] = len(
            turns
        )


        highest_escalation_score = 0

        highest_escalation_risk = (
            "Low"
        )


        for turn in turns:

            escalation = (
                turn.get(
                    "escalation",
                    {}
                )
                or {}
            )

            risk_score = (
                escalation.get(
                    "risk_score",
                    0
                )
            )

            risk_level = str(
                escalation.get(
                    "risk_level",
                    "Low"
                )
            ).strip()

            try:
                risk_score = int(
                    risk_score
                )

            except (
                TypeError,
                ValueError
            ):
                risk_score = 0

            if (
                risk_score
                >
                highest_escalation_score
            ):

                highest_escalation_score = (
                    risk_score
                )

                highest_escalation_risk = (
                    risk_level
                )


        summary[
            "highest_escalation_score"
        ] = highest_escalation_score

        summary[
            "highest_escalation_risk"
        ] = highest_escalation_risk


        final_evaluation = (
            turns[-1].get(
                "evaluation",
                {}
            )
            or {}
        )

        summary[
            "conversation_health"
        ] = final_evaluation.get(
            "conversation_health",
            "Unknown"
        )


        resolution_probability = (
            summary.get(
                "average_resolution_probability",
                0
            )
        )


        if resolution_probability >= 80:

            summary[
                "customer_outcome"
            ] = "Likely Resolved"

        elif resolution_probability >= 60:

            summary[
                "customer_outcome"
            ] = "Partially Resolved"

        else:

            summary[
                "customer_outcome"
            ] = "Needs Escalation"


        overall_score = (
            summary.get(
                "overall_score",
                0
            )
        )


        if overall_score >= 90:
            grade = "A+"

        elif overall_score >= 80:
            grade = "A"

        elif overall_score >= 70:
            grade = "B"

        elif overall_score >= 60:
            grade = "C"

        elif overall_score >= 50:
            grade = "D"

        else:
            grade = "Needs Improvement"


        summary[
            "grade"
        ] = grade


        session[
            "summary"
        ] = summary

        return summary


    def end_session(
        self,
        session_id
    ):
        """
        Completes a session
        and calculates summary.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            raise ValueError(
                "Session not found"
            )

        summary = (
            self.calculate_summary(
                session_id
            )
        )

        session[
            "status"
        ] = "Completed"

        session[
            "ended_at"
        ] = (
            datetime.now().isoformat()
        )

        return {

            "session":
                session,

            "summary":
                summary

        }


    def save_post_interaction_summary(
        self,
        session_id,
        post_summary
    ):
        """
        Stores AI-generated
        post-interaction summary.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            raise ValueError(
                "Session not found"
            )

        session[
            "post_interaction_summary"
        ] = (
            post_summary or {}
        )

        return session[
            "post_interaction_summary"
        ]


    def get_post_interaction_summary(
        self,
        session_id
    ):
        """
        Returns stored post-interaction
        AI summary.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            return {}

        return session.get(
            "post_interaction_summary",
            {}
        )


    def get_report_data(
        self,
        session_id
    ):
        """
        Returns complete report data.
        """

        session = self.get_session(
            session_id
        )

        if not session:
            raise ValueError(
                "Session not found"
            )

        if not session.get(
            "summary"
        ):
            self.calculate_summary(
                session_id
            )

        turns = session.get(
            "turns",
            []
        )

        report_data = {

            "session":
                session,

            "summary":
                session.get(
                    "summary",
                    {}
                ),

            "post_interaction_summary":
                session.get(
                    "post_interaction_summary",
                    {}
                ),

            "charts": {

                "turn_labels": [
                    f"Turn {turn.get('turn_number', i + 1)}"
                    for i, turn
                    in enumerate(turns)
                ],

                "overall_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "overall_score",
                        0
                    )
                    for turn in turns
                ],

                "empathy_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "empathy_score",
                        0
                    )
                    for turn in turns
                ],

                "clarity_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "clarity_score",
                        0
                    )
                    for turn in turns
                ],

                "tone_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "tone_score",
                        0
                    )
                    for turn in turns
                ],

                "policy_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "policy_accuracy",
                        0
                    )
                    for turn in turns
                ],

                "resolution_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "resolution_score",
                        0
                    )
                    for turn in turns
                ],

                "professionalism_scores": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "professionalism_score",
                        0
                    )
                    for turn in turns
                ],

                "resolution_probabilities": [
                    (
                        turn.get(
                            "evaluation",
                            {}
                        )
                        or {}
                    ).get(
                        "resolution_probability",
                        0
                    )
                    for turn in turns
                ],

                "frustration_levels": [
                    self._convert_frustration_to_score(
                        (
                            turn.get(
                                "customer_analysis",
                                {}
                            )
                            or {}
                        ).get(
                            "frustration_level",
                            "Medium"
                        )
                    )
                    for turn in turns
                ],

                "escalation_scores": [
                    (
                        turn.get(
                            "escalation",
                            {}
                        )
                        or {}
                    ).get(
                        "risk_score",
                        0
                    )
                    for turn in turns
                ]

            },

            "strengths":
                self._collect_feedback(
                    turns,
                    "strengths"
                ),

            "improvements":
                self._collect_feedback(
                    turns,
                    "improvements"
                ),

            "coaching_recommendations":
                self._collect_coaching_feedback(
                    turns
                ),

            "escalation_triggers":
                self._collect_escalation_reasons(
                    turns
                )

        }

        return report_data


    # =====================================================
    # MILESTONE 4
    # PERFORMANCE ANALYTICS
    # =====================================================

    def get_performance_analytics(
        self
    ):
        """
        Calculates analytics across
        multiple completed sessions.

        Returns:
        - overall trends
        - escalation triggers
        - knowledge gaps
        - improvement indicators
        - chart data
        """

        completed_sessions = [

            session

            for session
            in self.sessions.values()

            if (
                session.get(
                    "status"
                )
                ==
                "Completed"
            )

        ]


        if not completed_sessions:

            return {

                "total_sessions":
                    0,

                "average_score":
                    0,

                "performance_change":
                    0,

                "trend_direction":
                    "No Data",

                "common_escalation_triggers":
                    [],

                "knowledge_gaps":
                    [],

                "improvement_indicators":
                    {},

                "strongest_area":
                    "No Data",

                "weakest_area":
                    "No Data",

                "charts": {

                    "session_labels":
                        [],

                    "overall_scores":
                        [],

                    "empathy_scores":
                        [],

                    "clarity_scores":
                        [],

                    "tone_scores":
                        [],

                    "policy_scores":
                        [],

                    "resolution_scores":
                        [],

                    "professionalism_scores":
                        []

                }

            }


        # ---------------------------------------------
        # Make sure summaries exist
        # ---------------------------------------------

        for session in completed_sessions:

            if not session.get(
                "summary"
            ):

                self.calculate_summary(
                    session[
                        "session_id"
                    ]
                )


        # ---------------------------------------------
        # Sort sessions by completion time
        # ---------------------------------------------

        completed_sessions.sort(
            key=lambda item:
                item.get(
                    "ended_at"
                )
                or
                item.get(
                    "started_at",
                    ""
                )
        )


        overall_scores = [

            session.get(
                "summary",
                {}
            ).get(
                "overall_score",
                0
            )

            for session
            in completed_sessions

        ]


        average_score = round(
            sum(
                overall_scores
            )
            /
            len(
                overall_scores
            )
        )


        # ---------------------------------------------
        # Performance improvement trend
        # ---------------------------------------------

        if len(overall_scores) >= 2:

            performance_change = (
                overall_scores[-1]
                -
                overall_scores[0]
            )

        else:

            performance_change = 0


        if performance_change > 0:
            trend_direction = "Improving"

        elif performance_change < 0:
            trend_direction = "Declining"

        else:
            trend_direction = "Stable"


        # ---------------------------------------------
        # Collect metric averages
        # ---------------------------------------------

        metric_mapping = {

            "Empathy":
                "average_empathy",

            "Clarity":
                "average_clarity",

            "Tone":
                "average_tone",

            "Policy Accuracy":
                "average_policy_accuracy",

            "Resolution":
                "average_resolution",

            "Professionalism":
                "average_professionalism"

        }


        improvement_indicators = {}


        for (
            display_name,
            summary_key
        ) in metric_mapping.items():

            values = [

                session.get(
                    "summary",
                    {}
                ).get(
                    summary_key,
                    0
                )

                for session
                in completed_sessions

            ]


            metric_average = round(
                sum(values)
                /
                len(values)
            ) if values else 0


            change = 0


            if len(values) >= 2:

                change = (
                    values[-1]
                    -
                    values[0]
                )


            if change > 0:
                status = "Improving"

            elif change < 0:
                status = "Declining"

            else:
                status = "Stable"


            improvement_indicators[
                display_name
            ] = {

                "average":
                    metric_average,

                "change":
                    change,

                "status":
                    status

            }


        # ---------------------------------------------
        # Strongest / weakest areas
        # ---------------------------------------------

        if improvement_indicators:

            strongest_area = max(
                improvement_indicators,
                key=lambda key:
                    improvement_indicators[
                        key
                    ][
                        "average"
                    ]
            )

            weakest_area = min(
                improvement_indicators,
                key=lambda key:
                    improvement_indicators[
                        key
                    ][
                        "average"
                    ]
            )

        else:

            strongest_area = "No Data"

            weakest_area = "No Data"


        # ---------------------------------------------
        # Common escalation triggers
        # ---------------------------------------------

        escalation_counter = (
            Counter()
        )


        for session in completed_sessions:

            for turn in session.get(
                "turns",
                []
            ):

                escalation = (
                    turn.get(
                        "escalation",
                        {}
                    )
                    or {}
                )

                reasons = escalation.get(
                    "reasoning",
                    []
                )


                if isinstance(
                    reasons,
                    str
                ):

                    reasons = [
                        reasons
                    ]


                if not isinstance(
                    reasons,
                    list
                ):

                    continue


                for reason in reasons:

                    clean_reason = str(
                        reason or ""
                    ).strip()

                    if clean_reason:

                        escalation_counter[
                            clean_reason
                        ] += 1


        common_escalation_triggers = [

            {
                "trigger":
                    trigger,

                "count":
                    count
            }

            for (
                trigger,
                count
            )
            in escalation_counter
            .most_common(
                10
            )

        ]


        # ---------------------------------------------
        # Knowledge gaps
        # ---------------------------------------------

        knowledge_gap_counter = (
            Counter()
        )


        for session in completed_sessions:

            session_scenario = str(
                session.get(
                    "scenario",
                    "General Support"
                )
            ).strip()


            for turn in session.get(
                "turns",
                []
            ):

                knowledge = (
                    turn.get(
                        "knowledge",
                        {}
                    )
                    or {}
                )


                match_type = str(
                    knowledge.get(
                        "match_type",
                        ""
                    )
                ).strip().lower()


                source = str(
                    knowledge.get(
                        "source",
                        ""
                    )
                ).strip().lower()


                notice = str(
                    knowledge.get(
                        "notice",
                        ""
                    )
                ).strip().lower()


                is_gap = (

                    match_type
                    ==
                    "fallback"

                    or

                    "fallback"
                    in source

                    or

                    "no matching uploaded knowledge"
                    in notice

                    or

                    not knowledge

                )


                if is_gap:

                    knowledge_gap_counter[
                        session_scenario
                    ] += 1


        knowledge_gaps = [

            {
                "scenario":
                    scenario,

                "count":
                    count
            }

            for (
                scenario,
                count
            )
            in knowledge_gap_counter
            .most_common(
                10
            )

        ]


        # ---------------------------------------------
        # Multi-session charts
        # ---------------------------------------------

        session_labels = [

            f"Session {index + 1}"

            for index
            in range(
                len(
                    completed_sessions
                )
            )

        ]


        charts = {

            "session_labels":
                session_labels,

            "overall_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "overall_score",
                    0
                )

                for session
                in completed_sessions

            ],

            "empathy_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "average_empathy",
                    0
                )

                for session
                in completed_sessions

            ],

            "clarity_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "average_clarity",
                    0
                )

                for session
                in completed_sessions

            ],

            "tone_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "average_tone",
                    0
                )

                for session
                in completed_sessions

            ],

            "policy_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "average_policy_accuracy",
                    0
                )

                for session
                in completed_sessions

            ],

            "resolution_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "average_resolution",
                    0
                )

                for session
                in completed_sessions

            ],

            "professionalism_scores": [

                session.get(
                    "summary",
                    {}
                ).get(
                    "average_professionalism",
                    0
                )

                for session
                in completed_sessions

            ]

        }


        return {

            "total_sessions":
                len(
                    completed_sessions
                ),

            "average_score":
                average_score,

            "performance_change":
                performance_change,

            "trend_direction":
                trend_direction,

            "common_escalation_triggers":
                common_escalation_triggers,

            "knowledge_gaps":
                knowledge_gaps,

            "improvement_indicators":
                improvement_indicators,

            "strongest_area":
                strongest_area,

            "weakest_area":
                weakest_area,

            "charts":
                charts

        }


    def _convert_frustration_to_score(
        self,
        level
    ):
        """
        Converts frustration labels
        into chart values.
        """

        values = {

            "Low":
                25,

            "Medium":
                60,

            "High":
                90

        }

        normalized_level = str(
            level or "Medium"
        ).strip().title()

        return values.get(
            normalized_level,
            60
        )


    def _collect_feedback(
        self,
        turns,
        key
    ):
        """
        Collects unique strengths
        or improvements.
        """

        feedback = []

        for turn in turns:

            evaluation = (
                turn.get(
                    "evaluation",
                    {}
                )
                or {}
            )

            items = evaluation.get(
                key,
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
                    not in feedback
                ):
                    feedback.append(
                        clean_item
                    )

        return feedback


    def _collect_coaching_feedback(
        self,
        turns
    ):
        """
        Collects coaching recommendations
        from all turns.
        """

        recommendations = []

        for turn in turns:

            coaching = (
                turn.get(
                    "coaching",
                    {}
                )
                or {}
            )

            items = coaching.get(
                "improvement_tips",
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
                    not in recommendations
                ):
                    recommendations.append(
                        clean_item
                    )

        return recommendations


    def _collect_escalation_reasons(
        self,
        turns
    ):
        """
        Collects escalation reasons.
        """

        reasons = []

        for turn in turns:

            escalation = (
                turn.get(
                    "escalation",
                    {}
                )
                or {}
            )

            items = escalation.get(
                "reasoning",
                []
            )

            if isinstance(
                items,
                str
            ):
                items = [
                    items
                ]

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
                    not in reasons
                ):
                    reasons.append(
                        clean_item
                    )

        return reasons


    def list_sessions(
        self
    ):
        """
        Returns all sessions.
        """

        return list(
            self.sessions.values()
        )


session_manager = SessionManager()