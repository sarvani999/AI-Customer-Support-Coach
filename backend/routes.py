from flask import request, jsonify, render_template

from session.session_config import SessionConfig
from session.session_manager import session_manager

from agents.customer_simulator import CustomerSimulatorAgent
from agents.sentiment_agent import IntentSentimentAgent
from agents.knowledge_agent import KnowledgeRecommendationAgent
from agents.coaching_pipeline import CoachingPipeline
from agents.response_evaluator import ResponseEvaluator
from agents.orchestrator import AgentOrchestrator


simulator_agent = CustomerSimulatorAgent()
sentiment_agent = IntentSentimentAgent()
knowledge_agent = KnowledgeRecommendationAgent()
coaching_pipeline = CoachingPipeline()
response_evaluator = ResponseEvaluator()
orchestrator = AgentOrchestrator()


def get_json_data():
    """
    Safely reads JSON data from the frontend.
    """

    return request.get_json(silent=True) or {}


def get_knowledge(product, customer_message):
    """
    Retrieves knowledge while supporting different
    knowledge-agent method signatures.
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

        except Exception:
            return {}

    except Exception:
        return {}


def generate_next_customer_message(session):
    """
    Generates the next customer response using
    the language selected for the current session.
    """

    return simulator_agent.generate_message(
        session.get("product", "Amazon"),
        session.get("scenario", "General Support"),
        session.get(
            "customer_persona",
            "Regular Customer"
        ),
        session.get("language", "English")
    )


def register_routes(app):

    @app.route("/")
    def home():
        return render_template("index.html")


    @app.route("/session")
    def session_page():
        return render_template("session.html")


    @app.route("/simulator")
    def simulator_page():
        return render_template("simulator.html")


    @app.route("/report/<session_id>")
    def report_page(session_id):
        """
        Opens the report page for a completed session.
        """

        session = session_manager.get_session(session_id)

        if not session:
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


    @app.route("/create-session", methods=["POST"])
    def create_session():
        """
        Creates a tracked coaching session and generates
        the first customer message.
        """

        try:
            data = get_json_data()

            session_config = SessionConfig(**data)
            config_data = session_config.model_dump()

            product = config_data.get(
                "product",
                "Amazon"
            )

            scenario = config_data.get(
                "scenario",
                "General Support"
            )

            customer_persona = config_data.get(
                "customer_persona",
                "Regular Customer"
            )

            difficulty = config_data.get(
                "difficulty",
                "Medium"
            )

            language = config_data.get(
                "language",
                "English"
            )

            print("SELECTED LANGUAGE =", language)

            tracked_session = session_manager.create_session(
                product=product,
                scenario=scenario,
                customer_persona=customer_persona,
                difficulty=difficulty,
                language=language
            )

            first_customer_message = simulator_agent.generate_message(
                product,
                scenario,
                customer_persona,
                language
            )

            tracked_session["current_customer_message"] = (
                first_customer_message
            )

            return jsonify({
                "status": "success",
                "message": "Session created successfully",
                "session_id": tracked_session["session_id"],
                "session": tracked_session,
                "customer_message": first_customer_message
            }), 201

        except Exception as error:
            print("CREATE SESSION ERROR =", error)

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 400


    @app.route("/generate-message", methods=["POST"])
    def generate_message():
        """
        Generates a customer message.

        This route is retained for compatibility
        with the existing frontend.
        """

        try:
            data = get_json_data()

            product = data.get(
                "product",
                "Amazon"
            )

            scenario = data.get(
                "scenario",
                "General Support"
            )

            customer_persona = data.get(
                "customer_persona",
                "Regular Customer"
            )

            language = data.get(
                "language",
                "English"
            )

            print("GENERATE MESSAGE LANGUAGE =", language)

            message = simulator_agent.generate_message(
                product,
                scenario,
                customer_persona,
                language
            )

            return jsonify({
                "status": "success",
                "customer_message": message
            })

        except Exception as error:
            print("GENERATE MESSAGE ERROR =", error)

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 400


    @app.route("/analyze-message", methods=["POST"])
    def analyze_message():
        """
        Analyzes a customer message.

        This route is retained for compatibility
        with the existing frontend.
        """

        try:
            data = get_json_data()

            message = data.get(
                "message",
                ""
            ).strip()

            if not message:
                return jsonify({
                    "status": "error",
                    "message": "Customer message is required"
                }), 400

            result = sentiment_agent.analyze(message)

            return jsonify({
                "status": "success",
                "analysis": result
            })

        except Exception as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 400
    @app.route("/process-manual-message", methods=["POST"])
    def process_manual_message():
        """
        Processes a customer message and agent reply
        without creating a tracked session.

        This route is retained for compatibility
        with the existing frontend.
        """

        try:
            data = get_json_data()

            customer_message = data.get(
                "customer_message",
                ""
            ).strip()

            agent_reply = data.get(
                "agent_reply",
                ""
            ).strip()

            if not customer_message:
                return jsonify({
                    "status": "error",
                    "message": "Customer message is required"
                }), 400

            if not agent_reply:
                return jsonify({
                    "status": "error",
                    "message": "Agent reply is required"
                }), 400

            customer_analysis = sentiment_agent.analyze(
                customer_message
            )

            knowledge = orchestrator._retrieve_knowledge(
                data.get("product", "Amazon"),
                customer_message
            )

            evaluation = response_evaluator.evaluate(
                customer_message=customer_message,
                agent_reply=agent_reply,
                knowledge=knowledge
            )

            escalation = orchestrator.escalation_agent.check_risk(
                customer_analysis,
                customer_message
            )

            next_customer_message = simulator_agent.generate_message(
                data.get("product", "Amazon"),
                data.get("scenario", "General Support"),
                data.get(
                    "customer_persona",
                    "Regular Customer"
                ),
                data.get("language", "English")
            )

            return jsonify({
                "status": "success",
                "analysis": customer_analysis,
                "evaluation": evaluation,
                "knowledge": knowledge,
                "next_customer_message": next_customer_message,
                "escalation": escalation
            })

        except Exception as error:
            print("PROCESS MANUAL MESSAGE ERROR =", error)

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 500
    @app.route("/process-reply", methods=["POST"])
    def process_reply():
        """
        Main live-coaching route.

        Flow:
        1. Read customer message and agent reply.
        2. Analyze customer intent and sentiment.
        3. Retrieve relevant knowledge.
        4. Evaluate the agent reply.
        5. Store the conversation turn.
        6. Generate the next customer message.
        """

        try:
            data = get_json_data()

            session_id = data.get(
                "session_id",
                ""
            ).strip()

            customer_message = data.get(
                "customer_message",
                ""
            ).strip()

            agent_reply = data.get(
                "agent_reply",
                ""
            ).strip()

            if not session_id:
                return jsonify({
                    "status": "error",
                    "message": "Session ID is required"
                }), 400

            if not customer_message:
                return jsonify({
                    "status": "error",
                    "message": "Customer message is required"
                }), 400

            if not agent_reply:
                return jsonify({
                    "status": "error",
                    "message": "Agent reply is required"
                }), 400

            current_session = session_manager.get_session(
                session_id
            )

            if not current_session:
                return jsonify({
                    "status": "error",
                    "message": "Session not found"
                }), 404

            if current_session["status"] != "Active":
                return jsonify({
                    "status": "error",
                    "message": "This session is already completed"
                }), 400
            result = orchestrator.process_turn(
    session=current_session,
    customer_message=customer_message,
    agent_reply=agent_reply
)
            customer_analysis = result["customer_analysis"]
            knowledge = result["knowledge"]
            evaluation = result["evaluation"]
            next_customer_message = result["next_customer_message"]
            escalation = result["escalation"]
            print("EVALUATION =", evaluation)

            turn = session_manager.add_turn(
                session_id=session_id,
                customer_message=customer_message,
                agent_reply=agent_reply,
                customer_analysis=customer_analysis,
                evaluation=evaluation,
                knowledge=knowledge
            )
            current_session["current_customer_message"] = next_customer_message
            live_summary = session_manager.calculate_summary(
                session_id
            )

            print("LIVE SUMMARY =", live_summary)
            print(
                "CURRENT SESSION LANGUAGE =",
                current_session.get("language")
            )

            return jsonify({
                "status": "success",
                "message": "Reply evaluated successfully",
                "turn": turn,
                "analysis": customer_analysis,
                "evaluation": evaluation,
                "knowledge": knowledge,
                "next_customer_message": next_customer_message,
                "escalation": escalation,
                "live_summary": live_summary
            })

        except ValueError as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 404

        except Exception as error:
            print("PROCESS REPLY ERROR =", error)

            return jsonify({
                "status": "error",
                "message": str(error)
            }), 500


    @app.route("/end-session", methods=["POST"])
    def end_session():
        """
        Ends the session and prepares final report data.
        """

        try:
            data = get_json_data()

            session_id = data.get(
                "session_id",
                ""
            ).strip()

            if not session_id:
                return jsonify({
                    "status": "error",
                    "message": "Session ID is required"
                }), 400

            result = session_manager.end_session(session_id)

            return jsonify({
                "status": "success",
                "message": "Session completed successfully",
                "session_id": session_id,
                "summary": result["summary"],
                "report_url": f"/report/{session_id}"
            })

        except ValueError as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 404

        except Exception as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 500


    @app.route(
        "/session-report/<session_id>",
        methods=["GET"]
    )
    def session_report(session_id):
        """
        Returns complete report and chart data as JSON.
        """

        try:
            report_data = session_manager.get_report_data(
                session_id
            )

            return jsonify({
                "status": "success",
                "report": report_data
            })

        except ValueError as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 404

        except Exception as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 500


    @app.route("/sessions", methods=["GET"])
    def list_all_sessions():
        """
        Returns previous simulation sessions.
        """

        sessions = session_manager.list_sessions()

        return jsonify({
            "status": "success",
            "total_sessions": len(sessions),
            "sessions": sessions
        })


    @app.route("/run-coaching", methods=["POST"])
    def run_coaching():
        """
        Keeps the existing coaching-pipeline endpoint.
        """

        try:
            data = get_json_data()

            result = coaching_pipeline.run(
                data.get("product", "Amazon"),
                data.get(
                    "scenario",
                    "General Support"
                ),
                data.get(
                    "customer_persona",
                    "Regular Customer"
                )
            )

            return jsonify({
                "status": "success",
                "result": result
            })

        except Exception as error:
            return jsonify({
                "status": "error",
                "message": str(error)
            }), 500