import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)

try:
    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        system_instruction=(
            "You are a realistic Amazon customer simulator. "
            "Act only as the customer. "
            "Generate a natural customer-support message. "
            "Keep the response to one or two sentences."
        ),
        input=(
            "The customer received a damaged product and wants "
            "to request a return and refund. Generate the opening message."
        ),
    )

    print("\nGemini response:")
    print(interaction.output_text)

except Exception as error:
    error_message = str(error).lower()

    if "429" in error_message or "quota" in error_message:
        print(
            "\nGemini rate limit reached. "
            "Wait about one minute and run the file only once."
        )

    elif "high demand" in error_message or "500" in error_message:
        print(
            "\nGemini server is currently busy. "
            "Wait a few minutes and try again."
        )

    else:
        print("\nGemini error:")
        print(error)