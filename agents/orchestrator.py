from agents.customer_simulator import CustomerSimulatorAgent
from agents.sentiment_agent import IntentSentimentAgent
from agents.knowledge_agent import KnowledgeRecommendationAgent
from agents.response_evaluator import ResponseEvaluator
from agents.escalation_agent import EscalationAgent
from agents.coaching_agent import CoachingAgent


class AgentOrchestrator:
    """
    Coordinates all agents required to process
    one customer-support conversation turn.
    """

    def __init__(self):

        self.customer_simulator = (
            CustomerSimulatorAgent()
        )

        self.sentiment_agent = (
            IntentSentimentAgent()
        )

        self.knowledge_agent = (
            KnowledgeRecommendationAgent()
        )

        self.response_evaluator = (
            ResponseEvaluator()
        )

        self.escalation_agent = (
            EscalationAgent()
        )

        self.coaching_agent = (
            CoachingAgent()
        )


    def _retrieve_knowledge(
        self,
        product,
        customer_message,
        scenario=None
    ):
        """
        Retrieves the most relevant knowledge
        using product, scenario, and customer message.

        Also supports older knowledge-agent
        method signatures without breaking
        the application.
        """

        try:

            return (
                self.knowledge_agent
                .retrieve_knowledge(
                    product,
                    customer_message,
                    scenario
                )
            )

        except TypeError:

            try:

                return (
                    self.knowledge_agent
                    .retrieve_knowledge(
                        product,
                        customer_message
                    )
                )

            except TypeError:

                try:

                    return (
                        self.knowledge_agent
                        .retrieve_knowledge(
                            customer_message
                        )
                    )

                except Exception as error:

                    print(
                        "ORCHESTRATOR KNOWLEDGE ERROR =",
                        error
                    )

                    return {}

            except Exception as error:

                print(
                    "ORCHESTRATOR KNOWLEDGE ERROR =",
                    error
                )

                return {}

        except Exception as error:

            print(
                "ORCHESTRATOR KNOWLEDGE ERROR =",
                error
            )

            return {}


    def _get_conversation_history(
        self,
        session
    ):
        """
        Safely returns the stored conversation
        history for the current session.
        """

        conversation_history = (
            session.get(
                "conversation_history",
                []
            )
        )

        if not isinstance(
            conversation_history,
            list
        ):

            conversation_history = []

        return conversation_history


    def _store_conversation_turn(
        self,
        session,
        customer_message,
        agent_reply
    ):
        """
        Stores the latest customer and
        trainee messages in conversation history.

        This history is used by the customer
        simulator so the next customer response
        can continue naturally.
        """

        conversation_history = (
            self._get_conversation_history(
                session
            )
        )

        conversation_history.append(
            {
                "customer_message":
                    customer_message,

                "agent_reply":
                    agent_reply
            }
        )

        session[
            "conversation_history"
        ] = conversation_history

        return conversation_history


    def _generate_next_customer_message(
        self,
        session,
        conversation_history
    ):
        """
        Generates the next customer message.

        Simulator Mode:
        AI customer continues automatically.

        Manual Mode:
        Customer message can initially be entered
        manually and the AI customer can continue
        after the trainee responds.

        Replay Mode:
        No new AI customer message is generated
        because messages come from the transcript.
        """

        interaction_mode = str(
            session.get(
                "interaction_mode",
                "Simulator"
            )
        ).strip().lower()

        if interaction_mode == "replay":

            return ""

        try:

            next_customer_message = (
                self.customer_simulator
                .generate_message(
                    product=session.get(
                        "product",
                        "Amazon"
                    ),

                    scenario=session.get(
                        "scenario",
                        "General Support"
                    ),

                    persona=session.get(
                        "customer_persona",
                        "Regular Customer"
                    ),

                    language=session.get(
                        "language",
                        "English"
                    ),

                    difficulty=session.get(
                        "difficulty",
                        "Medium"
                    ),

                    conversation_history=
                        conversation_history,

                    session_id=session.get(
                        "session_id",
                        "default"
                    )
                )
            )

            return str(
                next_customer_message or ""
            ).strip()

        except Exception as error:

            print(
                "ORCHESTRATOR CUSTOMER "
                "SIMULATOR ERROR =",
                error
            )

            return ""


    def process_turn(
        self,
        session,
        customer_message,
        agent_reply
    ):
        """
        Runs the complete multi-agent pipeline
        for one customer-support turn.

        Flow:

        Customer Message
            ↓
        Intent & Sentiment Agent
            ↓
        Knowledge Recommendation Agent
            ↓
        Response Evaluator
            ↓
        Coaching Agent
            ↓
        Escalation Risk Agent
            ↓
        Conversation History
            ↓
        Next Customer Message
        """

        if not session:

            raise ValueError(
                "Session data is required"
            )


        customer_message = str(
            customer_message or ""
        ).strip()


        agent_reply = str(
            agent_reply or ""
        ).strip()


        if not customer_message:

            raise ValueError(
                "Customer message is required"
            )


        if not agent_reply:

            raise ValueError(
                "Agent reply is required"
            )


        # =================================================
        # STEP 1
        # Analyze customer intent, sentiment
        # and frustration.
        # =================================================

        try:

            customer_analysis = (
                self.sentiment_agent
                .analyze(
                    customer_message
                )
            )

        except Exception as error:

            print(
                "ORCHESTRATOR SENTIMENT ERROR =",
                error
            )

            customer_analysis = {}


        if not isinstance(
            customer_analysis,
            dict
        ):

            customer_analysis = {}


        # =================================================
        # STEP 2
        # Retrieve relevant knowledge using
        # product + scenario + customer message.
        # =================================================

        knowledge = (
            self._retrieve_knowledge(
                product=session.get(
                    "product",
                    "Amazon"
                ),

                customer_message=
                    customer_message,

                scenario=session.get(
                    "scenario",
                    "General Support"
                )
            )
        )


        if not isinstance(
            knowledge,
            dict
        ):

            knowledge = {}


        # =================================================
        # STEP 3
        # Evaluate the trainee's response.
        # =================================================

        try:

            evaluation = (
                self.response_evaluator
                .evaluate(
                    customer_message=
                        customer_message,

                    agent_reply=
                        agent_reply,

                    knowledge=
                        knowledge
                )
            )

        except Exception as error:

            print(
                "ORCHESTRATOR EVALUATION ERROR =",
                error
            )

            evaluation = {}


        if not isinstance(
            evaluation,
            dict
        ):

            evaluation = {}


        # =================================================
        # STEP 4
        # Generate coaching feedback.
        #
        # Coaching uses:
        # customer message
        # trainee reply
        # customer analysis
        # retrieved knowledge
        # evaluation result
        # =================================================

        try:

            coaching = (
                self.coaching_agent
                .generate_feedback(
                    customer_message=
                        customer_message,

                    agent_reply=
                        agent_reply,

                    customer_analysis=
                        customer_analysis,

                    knowledge=
                        knowledge,

                    evaluation=
                        evaluation
                )
            )

        except Exception as error:

            print(
                "ORCHESTRATOR COACHING ERROR =",
                error
            )

            coaching = {}


        if not isinstance(
            coaching,
            dict
        ):

            coaching = {}


        # =================================================
        # STEP 5
        # Calculate escalation risk.
        # =================================================

        try:

            escalation = (
                self.escalation_agent
                .check_risk(
                    customer_analysis,
                    customer_message
                )
            )

        except Exception as error:

            print(
                "ORCHESTRATOR ESCALATION ERROR =",
                error
            )

            escalation = {
                "risk_score": 0,
                "risk_level": "Low",
                "reasoning": []
            }


        if not isinstance(
            escalation,
            dict
        ):

            escalation = {
                "risk_score": 0,
                "risk_level": "Low",
                "reasoning": []
            }


        # =================================================
        # STEP 6
        # Store customer + trainee conversation
        # history for context.
        # =================================================

        conversation_history = (
            self._store_conversation_turn(
                session,
                customer_message,
                agent_reply
            )
        )


        # =================================================
        # STEP 7
        # Generate the next customer message.
        #
        # Simulator / Manual:
        # AI customer may continue.
        #
        # Replay:
        # Transcript controls the next message,
        # therefore AI generation is skipped.
        # =================================================

        next_customer_message = (
            self._generate_next_customer_message(
                session,
                conversation_history
            )
        )


        # =================================================
        # DEBUG OUTPUT
        # Useful while testing the complete pipeline.
        # =================================================

        print(
            "\n=============================="
        )

        print(
            "ORCHESTRATOR TURN RESULT"
        )

        print(
            "=============================="
        )


        print(
            "CUSTOMER ANALYSIS =",
            customer_analysis
        )


        print(
            "KNOWLEDGE =",
            knowledge
        )


        print(
            "EVALUATION =",
            evaluation
        )


        print(
            "COACHING =",
            coaching
        )


        print(
            "ESCALATION =",
            escalation
        )


        print(
            "NEXT CUSTOMER MESSAGE =",
            next_customer_message
        )


        print(
            "==============================\n"
        )


        # =================================================
        # FINAL ORCHESTRATOR OUTPUT
        #
        # routes.py receives this complete object.
        # It can then store evaluation, coaching,
        # escalation and knowledge in SessionManager.
        # =================================================

        return {

            "customer_analysis":
                customer_analysis,

            "knowledge":
                knowledge,

            "evaluation":
                evaluation,

            "coaching":
                coaching,

            "escalation":
                escalation,

            "next_customer_message":
                next_customer_message

        }