from sentiment_agent import IntentSentimentAgent


agent = IntentSentimentAgent()


message = "I am really disappointed with my Amazon order. I want to return it."


result = agent.analyze(message)


print("Analysis Result:")
print(result)