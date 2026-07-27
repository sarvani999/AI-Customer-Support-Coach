from agents.customer_simulator import CustomerSimulatorAgent
from agents.sentiment_agent import IntentSentimentAgent
from agents.knowledge_agent import KnowledgeRecommendationAgent



class CoachingPipeline:


    def __init__(self):

        self.customer_agent = CustomerSimulatorAgent()

        self.sentiment_agent = IntentSentimentAgent()

        self.knowledge_agent = KnowledgeRecommendationAgent()



    def run(
        self,
        product,
        scenario,
        persona
    ):


        customer_message = self.customer_agent.generate_message(

            product,

            scenario,

            persona

        )


        analysis = self.sentiment_agent.analyze(

            customer_message

        )


        knowledge = self.knowledge_agent.retrieve_knowledge(

            customer_message

        )


        return {

            "customer_message": customer_message,

            "analysis": analysis,

            "knowledge": knowledge

        }