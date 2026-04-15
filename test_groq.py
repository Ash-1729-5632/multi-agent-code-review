from groq import Groq
from dotenv import load_dotenv
import os

# Load your .env file
load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    # Send a simple test message using a CURRENT 2026 model
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say: Groq is working!"}]
    )

    # Print the result
    print("\n--- Live API Test ---")
    print(f"Response: {response.choices[0].message.content}")
    print("Status: Success! Your AI is officially connected. ✅")
    print("---------------------\n")

except Exception as e:
    print(f"\n❌ API Test Failed: {e}")