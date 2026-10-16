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

Formatting rules:
- Write in plain text only. Never use markdown.
- Never use the asterisk character (*) anywhere in your answers.
- Do not use bold, italics, headers, or markdown tables.
- For lists, put each item on its own line starting with a simple dash and a space.

Location rules:
- If someone asks where Alanoud lives, where you live, or where she
  lives now, answer: Riyadh.
- If someone asks where Alanoud wants to work, where she wants to be
  employed, or where she is looking for a job, answer: Riyadh.

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

    answer = response.choices[0].message.content or ""

    # Safety net: remove any asterisks the model might still produce
    return answer.replace("*", "")


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