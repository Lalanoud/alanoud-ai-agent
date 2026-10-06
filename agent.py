from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / ".env")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-120b"

with open(Path(__file__).parent / "profile.txt", "r", encoding="utf-8") as file:
    profile = file.read()

instructions = f"""
You are Alanoud Alotaibi's AI portfolio assistant.

Answer questions about Alanoud using ONLY the information in the profile below.

Do not invent information.

If the information is not available, say:
"I don't have that information about Alanoud."

Keep your answers clear, friendly, and professional.

Alanoud's profile:
{profile}
"""

def ask_agent(question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": question}
        ],
    )

    return response.choices[0].message.content


print("Alanoud AI Assistant")
print("Type 'exit' to stop.\n")

while True:
    question = input("You: ")

    if question.lower() == "exit":
        break

    try:
        answer = ask_agent(question)
        print("\nAI:", answer, "\n")
    except Exception as e:
        print("\nError:", e, "\n")