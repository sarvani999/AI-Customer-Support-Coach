from coaching_pipeline import CoachingPipeline



pipeline = CoachingPipeline()



scenarios = [

    {
        "product": "Amazon",
        "scenario": "Return Request",
        "persona": "Frustrated"
    },


    {
        "product": "Amazon",
        "scenario": "Delivery Delay",
        "persona": "Angry"
    },


    {
        "product": "Amazon",
        "scenario": "Refund Issue",
        "persona": "Confused"
    },


    {
        "product": "Amazon",
        "scenario": "Order Cancellation",
        "persona": "Frustrated"
    }

]



for index, item in enumerate(scenarios, start=1):


    print("\n==============================")

    print("Scenario", index)

    print("==============================")


    result = pipeline.run(

        item["product"],

        item["scenario"],

        item["persona"]

    )


    print("\nCustomer Message:")

    print(result["customer_message"])



    print("\nAnalysis:")

    print(result["analysis"])



    print("\nKnowledge Recommendation:")

    print(result["knowledge"])