import os
import chromadb
import crewai
from groq import Groq
from dotenv import load_dotenv

# Load the keys from your .env file
load_dotenv()

print("\n--- Project Setup Verification ---")

# 1. Check Imports
print("✅ All libraries imported successfully!")

# 2. Check Groq Key
groq_key = os.getenv('GROQ_API_KEY')
if groq_key and groq_key.startswith('gsk_'):
    print(f"✅ Groq API Key found: Yes (Ends in ...{groq_key[-4:]})")
else:
    print("❌ Groq API Key NOT found or invalid. Check your .env file!")

# 3. Check Library Versions
print(f"✅ ChromaDB version: {chromadb.__version__}")
print(f"✅ CrewAI version: {crewai.__version__}")

print("----------------------------------\n")