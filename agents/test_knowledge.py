from knowledge_agent import KnowledgeRecommendationAgent



agent = KnowledgeRecommendationAgent()



message = "I want to return my Amazon order"



result = agent.retrieve_knowledge(message)



print("Knowledge Recommendation:")

print(result)