from customer_simulator import CustomerSimulatorAgent


agent = CustomerSimulatorAgent()


product = "Amazon"

scenario = "Return Request"

persona = "Frustrated"



for i in range(3):

    message = agent.generate_message(
        product,
        scenario,
        persona
    )

    print("Customer:")
    print(message)
    print()