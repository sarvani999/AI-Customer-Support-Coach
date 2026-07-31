from agents.customer_simulator import CustomerSimulatorAgent
from agents.sentiment_agent import IntentSentimentAgent
from agents.knowledge_agent import KnowledgeRecommendationAgent
from agents.response_evaluator import ResponseEvaluator
from agents.escalation_agent import EscalationAgent


class AgentOrchestrator:
    """
    Coordinates all agents required to process
    one customer-support conversation turn.
    """

    def __init__(self):
        self.customer_simulator = CustomerSimulatorAgent()
        self.sentiment_agent = IntentSentimentAgent()
        self.knowledge_agent = KnowledgeRecommendationAgent()
        self.response_evaluator = ResponseEvaluator()
        self.escalation_agent = EscalationAgent()
    def _retrieve_knowledge(self, product, customer_message):
        """
        Supports the current knowledge-agent method and
        future product-based retrieval without breaking the app.
        """

        try:
            return self.knowledge_agent.retrieve_knowledge(
                product,
                customer_message
            )

        except TypeError:
            return self.knowledge_agent.retrieve_knowledge(
                customer_message
            )

    def process_turn(
        self,
        session,
        customer_message,
        agent_reply
    ):
        """
        Runs the complete processing flow for one turn.

        Flow:
        1. Analyze customer intent and sentiment.
        2. Retrieve relevant knowledge.
        3. Evaluate the support agent's response.
        4. Generate the next customer message.
        5. Return all results in one structured response.
        """

        if not session:
            raise ValueError("Session data is required")

        customer_message = str(customer_message).strip()
        agent_reply = str(agent_reply).strip()

        if not customer_message:
            raise ValueError("Customer message is required")

        if not agent_reply:
            raise ValueError("Agent reply is required")

        customer_analysis = self.sentiment_agent.analyze(
            customer_message
        )

        knowledge = self._retrieve_knowledge(
            session.get("product", "Amazon"),
            customer_message
        )

        evaluation = self.response_evaluator.evaluate(
            customer_message=customer_message,
            agent_reply=agent_reply,
            knowledge=knowledge
        )
        escalation = self.escalation_agent.check_risk(
            customer_analysis,
            customer_message
            )
        next_customer_message = (
            self.customer_simulator.generate_message(
                session.get("product", "Amazon"),
                session.get("scenario", "General Support"),
                session.get(
                    "customer_persona",
                    "Regular Customer"
                ),
                session.get("language", "English")
            )
        )

        return {
            "customer_analysis": customer_analysis,
            "knowledge": knowledge,
            "evaluation": evaluation,
            "next_customer_message": next_customer_message,
            "escalation": escalation
        }