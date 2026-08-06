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
        customer_message
    ):
        """
        Supports different knowledge-agent method
        signatures without breaking the application.
        """

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


    def _get_conversation_history(
        self,
        session
    ):
        """
        Safely returns the stored conversation
        history for the current session.
        """

        conversation_history = session.get(
            "conversation_history",
            []
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
        Stores the latest customer and agent messages
        so the AI customer can continue naturally.
        """

        conversation_history = (
            self._get_conversation_history(
                session
            )
        )

        conversation_history.append({
            "customer_message":
                customer_message,
            "agent_reply":
                agent_reply
        })

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
        Generates the next AI customer message.

        Simulator Mode:
        AI customer continues automatically.

        Manual Mode:
        The first customer message may be entered
        manually, but after the agent replies,
        the AI customer continues the conversation.

        Replay Mode:
        No new AI customer message is generated.
        """

        interaction_mode = str(
            session.get(
                "interaction_mode",
                "Simulator"
            )
        ).strip().lower()

        if interaction_mode == "replay":
            return ""

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

    def process_turn(
        self,
        session,
        customer_message,
        agent_reply
    ):
        """
        Runs the complete processing flow
        for one customer-support turn.
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

        customer_analysis = (
            self.sentiment_agent.analyze(
                customer_message
            )
        )

        knowledge = self._retrieve_knowledge(
            session.get(
                "product",
                "Amazon"
            ),
            customer_message
        )

        evaluation = (
            self.response_evaluator.evaluate(
                customer_message=
                    customer_message,
                agent_reply=
                    agent_reply,
                knowledge=
                    knowledge
            )
        )

        coaching = (
            self.coaching_agent.generate_feedback(
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

        escalation = (
            self.escalation_agent.check_risk(
                customer_analysis,
                customer_message
            )
        )

        conversation_history = (
            self._store_conversation_turn(
                session,
                customer_message,
                agent_reply
            )
        )

        next_customer_message = (
            self._generate_next_customer_message(
                session,
                conversation_history
            )
        )

        print(
            "ORCHESTRATOR ANALYSIS =",
            customer_analysis
        )

        print(
            "ORCHESTRATOR KNOWLEDGE =",
            knowledge
        )

        print(
            "ORCHESTRATOR EVALUATION =",
            evaluation
        )

        print(
            "ORCHESTRATOR COACHING =",
            coaching
        )

        print(
            "ORCHESTRATOR ESCALATION =",
            escalation
        )

        print(
            "ORCHESTRATOR NEXT CUSTOMER MESSAGE =",
            next_customer_message
        )

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