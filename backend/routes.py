from flask import jsonify, render_template, request

from session.session_config import SessionConfig
from session.session_manager import session_manager

from agents.coaching_pipeline import CoachingPipeline
from agents.customer_simulator import CustomerSimulatorAgent
from agents.knowledge_agent import KnowledgeRecommendationAgent
from agents.orchestrator import AgentOrchestrator
from agents.response_evaluator import ResponseEvaluator
from agents.sentiment_agent import IntentSentimentAgent


# =========================================================
# AGENT OBJECTS
# =========================================================

simulator_agent = CustomerSimulatorAgent()
sentiment_agent = IntentSentimentAgent()
knowledge_agent = KnowledgeRecommendationAgent()
coaching_pipeline = CoachingPipeline()
response_evaluator = ResponseEvaluator()
orchestrator = AgentOrchestrator()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_json_data():
    """
    Safely reads JSON data from the frontend.
    """

    return request.get_json(
        silent=True
    ) or {}


def get_knowledge(
    product,
    customer_message
):
    """
    Retrieves relevant knowledge while supporting
    different knowledge-agent method signatures.
    """

    try:
        return knowledge_agent.retrieve_knowledge(
            product,
            customer_message
        )

    except TypeError:

        try:
            return knowledge_agent.retrieve_knowledge(
                customer_message
            )

        except Exception as error:
            print(
                "KNOWLEDGE ERROR =",
                error
            )

            return {}

    except Exception as error:
        print(
            "KNOWLEDGE ERROR =",
            error
        )

        return {}


def get_active_session(
    session_id
):
    """
    Returns an active session or raises
    a clear validation error.
    """

    if not session_id:
        raise ValueError(
            "Session ID is required"
        )

    current_session = (
        session_manager.get_session(
            session_id
        )
    )

    if not current_session:
        raise LookupError(
            "Session not found"
        )

    if (
        current_session.get(
            "status"
        )
        != "Active"
    ):
        raise ValueError(
            "This session is already completed"
        )

    return current_session


def generate_opening_customer_message(
    tracked_session
):
    """
    Generates the first customer message
    depending on interaction mode.
    """

    interaction_mode = str(
        tracked_session.get(
            "interaction_mode",
            "Simulator"
        )
    ).strip().lower()

    if interaction_mode == "manual":
        return ""

    if interaction_mode == "replay":
        return (
            "Upload a transcript "
            "to begin replay coaching."
        )

    return simulator_agent.generate_message(
        product=tracked_session.get(
            "product",
            "Amazon"
        ),
        scenario=tracked_session.get(
            "scenario",
            "General Support"
        ),
        persona=tracked_session.get(
            "customer_persona",
            "Regular Customer"
        ),
        language=tracked_session.get(
            "language",
            "English"
        ),
        difficulty=tracked_session.get(
            "difficulty",
            "Medium"
        ),
        conversation_history=[],
        session_id=tracked_session.get(
            "session_id",
            "default"
        )
    )


# =========================================================
# ROUTES
# =========================================================

def register_routes(app):

    # -----------------------------------------------------
    # PAGE ROUTES
    # -----------------------------------------------------

    @app.route("/")
    def home():
        return render_template(
            "index.html"
        )


    @app.route("/session")
    def session_page():
        return render_template(
            "session.html"
        )


    @app.route("/simulator")
    def simulator_page():
        return render_template(
            "simulator.html"
        )


    @app.route(
        "/report/<session_id>"
    )
    def report_page(
        session_id
    ):
        """
        Opens the final report page.
        """

        current_session = (
            session_manager.get_session(
                session_id
            )
        )

        if not current_session:

            return render_template(
                "report.html",
                session_id=session_id,
                session_found=False
            ), 404

        return render_template(
            "report.html",
            session_id=session_id,
            session_found=True
        )


    # -----------------------------------------------------
    # CREATE SESSION
    # -----------------------------------------------------

    @app.route(
        "/create-session",
        methods=["POST"]
    )
    def create_session():
        """
        Creates a Simulator, Manual,
        or Replay coaching session.
        """

        try:
            data = get_json_data()

            session_config = (
                SessionConfig(**data)
            )

            config_data = (
                session_config.model_dump()
            )

            interaction_mode = str(
                config_data.get(
                    "interaction_mode",
                    "Simulator"
                )
            ).strip()

            product = str(
                config_data.get(
                    "product",
                    "Amazon"
                )
            ).strip()

            scenario = str(
                config_data.get(
                    "scenario",
                    "General Support"
                )
            ).strip()

            customer_persona = str(
                config_data.get(
                    "customer_persona",
                    "Regular Customer"
                )
            ).strip()

            difficulty = str(
                config_data.get(
                    "difficulty",
                    "Medium"
                )
            ).strip()

            language = str(
                config_data.get(
                    "language",
                    "English"
                )
            ).strip()

            tracked_session = (
                session_manager.create_session(
                    interaction_mode=
                        interaction_mode,
                    product=
                        product,
                    scenario=
                        scenario,
                    customer_persona=
                        customer_persona,
                    difficulty=
                        difficulty,
                    language=
                        language
                )
            )

            tracked_session[
                "conversation_history"
            ] = []

            tracked_session[
                "previous_escalation_score"
            ] = 0

            first_customer_message = (
                generate_opening_customer_message(
                    tracked_session
                )
            )

            tracked_session[
                "current_customer_message"
            ] = first_customer_message

            print(
                "SELECTED INTERACTION MODE =",
                interaction_mode
            )

            print(
                "SELECTED LANGUAGE =",
                language
            )

            print(
                "OPENING CUSTOMER MESSAGE =",
                first_customer_message
            )

            return jsonify({
                "status":
                    "success",
                "message":
                    "Session created successfully",
                "session_id":
                    tracked_session[
                        "session_id"
                    ],
                "session":
                    tracked_session,
                "customer_message":
                    first_customer_message
            }), 201

        except Exception as error:

            print(
                "CREATE SESSION ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 400
            # -----------------------------------------------------
    # NEXT TURN (NEW AI CONVERSATION FLOW)
    # -----------------------------------------------------

    @app.route(
        "/next-turn",
        methods=["POST"]
    )
    def next_turn():
        """
        Runs one complete AI conversation turn.

        Flow:
        Customer Message
              ↓
        Analysis
              ↓
        Knowledge
              ↓
        Evaluation
              ↓
        Coaching
              ↓
        Escalation
              ↓
        Next AI Customer Message
        """

        try:

            data = get_json_data()

            session_id = str(
                data.get(
                    "session_id",
                    ""
                )
            ).strip()

            agent_reply = str(
                data.get(
                    "agent_reply",
                    ""
                )
            ).strip()

            current_session = (
                get_active_session(
                    session_id
                )
            )

            customer_message = str(
                current_session.get(
                    "current_customer_message",
                    ""
                )
            ).strip()

            if not customer_message:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Customer message is empty."
                }), 400

            result = (
                orchestrator.process_turn(
                    session=current_session,
                    customer_message=
                        customer_message,
                    agent_reply=
                        agent_reply
                )
            )

            current_session[
                "current_customer_message"
            ] = result.get(
                "next_customer_message",
                ""
            )

            return jsonify({

                "status":
                    "success",

                "customer_message":
                    result.get(
                        "next_customer_message",
                        ""
                    ),

                "analysis":
                    result.get(
                        "customer_analysis",
                        {}
                    ),

                "knowledge":
                    result.get(
                        "knowledge",
                        {}
                    ),

                "evaluation":
                    result.get(
                        "evaluation",
                        {}
                    ),

                "coaching":
                    result.get(
                        "coaching",
                        {}
                    ),

                "escalation":
                    result.get(
                        "escalation",
                        {}
                    )

            }), 200

        except LookupError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 404

        except Exception as error:

            print(
                "NEXT TURN ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500
            # -----------------------------------------------------
    # PROCESS REPLY
    # -----------------------------------------------------

    @app.route(
        "/process-reply",
        methods=["POST"]
    )
    def process_reply():
        """
        Compatibility endpoint used by the
        current simulator frontend.

        It runs the same complete AI conversation
        flow as /next-turn.
        """

        try:
            data = get_json_data()

            session_id = str(
                data.get(
                    "session_id",
                    ""
                )
            ).strip()

            agent_reply = str(
                data.get(
                    "agent_reply",
                    ""
                )
            ).strip()

            if not session_id:

                return jsonify({
                    "status": "error",
                    "message":
                        "Session ID is required"
                }), 400

            if not agent_reply:

                return jsonify({
                    "status": "error",
                    "message":
                        "Agent reply is required"
                }), 400

            current_session = (
                get_active_session(
                    session_id
                )
            )

            customer_message = str(
                data.get(
                    "customer_message"
                )
                or current_session.get(
                    "current_customer_message",
                    ""
                )
            ).strip()

            if not customer_message:

                return jsonify({
                    "status": "error",
                    "message":
                        "Customer message is required"
                }), 400

            result = (
                orchestrator.process_turn(
                    session=current_session,
                    customer_message=
                        customer_message,
                    agent_reply=
                        agent_reply
                )
            )

            customer_analysis = (
                result.get(
                    "customer_analysis",
                    {}
                )
            )

            knowledge = result.get(
                "knowledge",
                {}
            )

            evaluation = result.get(
                "evaluation",
                {}
            )

            coaching = result.get(
                "coaching",
                {}
            )

            escalation = result.get(
                "escalation",
                {}
            )

            next_customer_message = str(
                result.get(
                    "next_customer_message",
                    ""
                )
                or ""
            ).strip()

            current_session[
                "current_customer_message"
            ] = next_customer_message

            current_session[
                "previous_escalation_score"
            ] = escalation.get(
                "risk_score",
                0
            )

            turn = (
                session_manager.add_turn(
                    session_id=
                        session_id,
                    customer_message=
                        customer_message,
                    agent_reply=
                        agent_reply,
                    customer_analysis=
                        customer_analysis,
                    evaluation=
                        evaluation,
                    knowledge=
                        knowledge
                )
            )

            turn["coaching"] = (
                coaching
            )

            turn["escalation"] = (
                escalation
            )

            turn[
                "ai_suggestion_used"
            ] = bool(
                data.get(
                    "ai_suggestion_used",
                    False
                )
            )

            turn[
                "suggested_response"
            ] = str(
                data.get(
                    "suggested_response",
                    ""
                )
            ).strip()

            live_summary = (
                session_manager.calculate_summary(
                    session_id
                )
            )

            print(
                "CURRENT CUSTOMER MESSAGE =",
                customer_message
            )

            print(
                "AGENT REPLY =",
                agent_reply
            )

            print(
                "NEXT AI CUSTOMER MESSAGE =",
                next_customer_message
            )

            return jsonify({
                "status":
                    "success",
                "message":
                    "Reply processed successfully",
                "turn":
                    turn,
                "analysis":
                    customer_analysis,
                "evaluation":
                    evaluation,
                "coaching":
                    coaching,
                "knowledge":
                    knowledge,
                "escalation":
                    escalation,
                "next_customer_message":
                    next_customer_message,
                "live_summary":
                    live_summary
            }), 200

        except LookupError as error:

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 404

        except ValueError as error:

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 400

        except Exception as error:

            print(
                "PROCESS REPLY ERROR =",
                error
            )

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 500
            # -----------------------------------------------------
    # MANUAL MODE MESSAGE ANALYSIS
    # -----------------------------------------------------

    @app.route(
        "/process-manual-message",
        methods=["POST"]
    )
    def process_manual_message():
        """
        Processes a manually entered customer message.

        Flow:
        1. Analyze customer message.
        2. Retrieve relevant knowledge.
        3. Calculate escalation risk.
        4. Store message as the current customer message.
        """

        try:
            data = get_json_data()

            session_id = str(
                data.get(
                    "session_id",
                    ""
                )
            ).strip()

            customer_message = str(
                data.get(
                    "customer_message"
                )
                or data.get(
                    "message"
                )
                or ""
            ).strip()

            if not customer_message:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Customer message is required"
                }), 400

            current_session = None

            if session_id:

                current_session = (
                    get_active_session(
                        session_id
                    )
                )

            if current_session:

                product = str(
                    current_session.get(
                        "product",
                        "Amazon"
                    )
                ).strip()

            else:

                product = str(
                    data.get(
                        "product",
                        "Amazon"
                    )
                ).strip()

            customer_analysis = (
                sentiment_agent.analyze(
                    customer_message
                )
            )

            knowledge = get_knowledge(
                product,
                customer_message
            )

            escalation = (
                orchestrator
                .escalation_agent
                .check_risk(
                    customer_analysis,
                    customer_message
                )
            )

            if current_session:

                current_session[
                    "current_customer_message"
                ] = customer_message

            print(
                "MANUAL CUSTOMER MESSAGE =",
                customer_message
            )

            print(
                "MANUAL CUSTOMER ANALYSIS =",
                customer_analysis
            )

            return jsonify({
                "status":
                    "success",
                "customer_message":
                    customer_message,
                "analysis":
                    customer_analysis,
                "knowledge":
                    knowledge,
                "escalation":
                    escalation
            }), 200

        except LookupError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 404

        except ValueError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 400

        except Exception as error:

            print(
                "PROCESS MANUAL MESSAGE ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    # -----------------------------------------------------
    # GENERATE AI SUGGESTED AGENT REPLY
    # -----------------------------------------------------

    @app.route(
        "/generate-suggested-reply",
        methods=["POST"]
    )
    def generate_suggested_reply():
        """
        Generates an AI support-agent reply
        before the trainee sends a response.
        """

        try:
            data = get_json_data()

            session_id = str(
                data.get(
                    "session_id",
                    ""
                )
            ).strip()

            customer_message = str(
                data.get(
                    "customer_message"
                )
                or data.get(
                    "message"
                )
                or ""
            ).strip()

            if not customer_message:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Customer message is required"
                }), 400

            current_session = None

            if session_id:

                current_session = (
                    get_active_session(
                        session_id
                    )
                )

            if current_session:

                product = str(
                    current_session.get(
                        "product",
                        "Amazon"
                    )
                ).strip()

            else:

                product = str(
                    data.get(
                        "product",
                        "Amazon"
                    )
                ).strip()

            customer_analysis = (
                data.get(
                    "analysis"
                )
                or data.get(
                    "customer_analysis"
                )
                or sentiment_agent.analyze(
                    customer_message
                )
            )

            knowledge = (
                data.get(
                    "knowledge"
                )
                or get_knowledge(
                    product,
                    customer_message
                )
            )

            suggestion = (
                orchestrator
                .coaching_agent
                .suggest_response(
                    customer_message=
                        customer_message,
                    customer_analysis=
                        customer_analysis,
                    knowledge=
                        knowledge
                )
            )

            suggested_response = str(
                suggestion.get(
                    "suggested_response",
                    ""
                )
            ).strip()

            if not suggested_response:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "AI suggestion was empty"
                }), 500

            return jsonify({
                "status":
                    "success",
                "source":
                    suggestion.get(
                        "source",
                        "gemini"
                    ),
                "suggested_response":
                    suggested_response,
                "reasoning":
                    suggestion.get(
                        "reasoning",
                        ""
                    ),
                "analysis":
                    customer_analysis,
                "knowledge":
                    knowledge
            }), 200

        except LookupError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 404

        except ValueError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 400

        except Exception as error:

            print(
                "GENERATE SUGGESTED REPLY ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500
            # -----------------------------------------------------
    # GENERATE CUSTOMER MESSAGE
    # -----------------------------------------------------

    @app.route(
        "/generate-message",
        methods=["POST"]
    )
    def generate_message():
        """
        Generates a fresh AI customer message.
        """

        try:
            data = get_json_data()

            session_id = str(
                data.get(
                    "session_id",
                    ""
                )
            ).strip()

            current_session = None

            if session_id:
                current_session = (
                    get_active_session(
                        session_id
                    )
                )

            if current_session:
                product = current_session.get(
                    "product",
                    "Amazon"
                )

                scenario = current_session.get(
                    "scenario",
                    "General Support"
                )

                persona = current_session.get(
                    "customer_persona",
                    "Regular Customer"
                )

                language = current_session.get(
                    "language",
                    "English"
                )

                difficulty = current_session.get(
                    "difficulty",
                    "Medium"
                )

                conversation_history = (
                    current_session.get(
                        "conversation_history",
                        []
                    )
                )

            else:
                product = data.get(
                    "product",
                    "Amazon"
                )

                scenario = data.get(
                    "scenario",
                    "General Support"
                )

                persona = data.get(
                    "customer_persona",
                    "Regular Customer"
                )

                language = data.get(
                    "language",
                    "English"
                )

                difficulty = data.get(
                    "difficulty",
                    "Medium"
                )

                conversation_history = (
                    data.get(
                        "conversation_history",
                        []
                    )
                )

            customer_message = (
                simulator_agent.generate_message(
                    product=product,
                    scenario=scenario,
                    persona=persona,
                    language=language,
                    difficulty=difficulty,
                    conversation_history=
                        conversation_history,
                    session_id=
                        session_id or "default"
                )
            )

            if current_session:
                current_session[
                    "current_customer_message"
                ] = customer_message

            return jsonify({
                "status":
                    "success",
                "customer_message":
                    customer_message
            }), 200

        except LookupError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 404

        except Exception as error:

            print(
                "GENERATE MESSAGE ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    # -----------------------------------------------------
    # ANALYZE MESSAGE
    # -----------------------------------------------------

    @app.route(
        "/analyze-message",
        methods=["POST"]
    )
    def analyze_message():
        """
        Analyzes intent, sentiment,
        and frustration.
        """

        try:
            data = get_json_data()

            customer_message = str(
                data.get(
                    "customer_message"
                )
                or data.get(
                    "message"
                )
                or ""
            ).strip()

            if not customer_message:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Customer message is required"
                }), 400

            analysis = (
                sentiment_agent.analyze(
                    customer_message
                )
            )

            return jsonify({
                "status":
                    "success",
                "analysis":
                    analysis
            }), 200

        except Exception as error:

            print(
                "ANALYZE MESSAGE ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    # -----------------------------------------------------
    # END SESSION
    # -----------------------------------------------------

    @app.route(
        "/end-session",
        methods=["POST"]
    )
    def end_session():
        """
        Ends the active session.
        """

        try:
            data = get_json_data()

            session_id = str(
                data.get(
                    "session_id",
                    ""
                )
            ).strip()

            if not session_id:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Session ID is required"
                }), 400

            result = (
                session_manager.end_session(
                    session_id
                )
            )

            simulator_agent.reset_session(
                session_id
            )

            return jsonify({
                "status":
                    "success",
                "message":
                    "Session completed successfully",
                "session_id":
                    session_id,
                "summary":
                    result["summary"],
                "report_url":
                    f"/report/{session_id}"
            }), 200

        except ValueError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 404

        except Exception as error:

            print(
                "END SESSION ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    # -----------------------------------------------------
    # SESSION REPORT
    # -----------------------------------------------------

    @app.route(
        "/session-report/<session_id>",
        methods=["GET"]
    )
    def session_report(
        session_id
    ):
        """
        Returns the complete session report.
        """

        try:
            report_data = (
                session_manager.get_report_data(
                    session_id
                )
            )

            return jsonify({
                "status":
                    "success",
                "report":
                    report_data
            }), 200

        except ValueError as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 404

        except Exception as error:

            print(
                "SESSION REPORT ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    # -----------------------------------------------------
    # LIST SESSIONS
    # -----------------------------------------------------

    @app.route(
        "/sessions",
        methods=["GET"]
    )
    def list_all_sessions():
        """
        Returns all sessions.
        """

        try:
            sessions = (
                session_manager.list_sessions()
            )

            return jsonify({
                "status":
                    "success",
                "total_sessions":
                    len(sessions),
                "sessions":
                    sessions
            }), 200

        except Exception as error:

            print(
                "LIST SESSIONS ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    # -----------------------------------------------------
    # LEGACY COACHING PIPELINE
    # -----------------------------------------------------

    @app.route(
        "/run-coaching",
        methods=["POST"]
    )
    def run_coaching():
        """
        Keeps the previous coaching endpoint
        for compatibility.
        """

        try:
            data = get_json_data()

            result = (
                coaching_pipeline.run(
                    data.get(
                        "product",
                        "Amazon"
                    ),
                    data.get(
                        "scenario",
                        "General Support"
                    ),
                    data.get(
                        "customer_persona",
                        "Regular Customer"
                    )
                )
            )

            return jsonify({
                "status":
                    "success",
                "result":
                    result
            }), 200

        except Exception as error:

            print(
                "RUN COACHING ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500