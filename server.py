from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-120b"

# Load Alanoud's information
with open(
    Path(__file__).parent / "profile.txt",
    "r",
    encoding="utf-8"
) as file:
    profile = file.read()

instructions = f"""
You are Alanoud Alotaibi's AI portfolio assistant.

Your job is to answer questions about Alanoud, her education,
skills, experience, projects, and career interests.

Use ONLY the information provided in the profile below.

Do not invent information.
Do not claim that Alanoud has experience, skills, certifications,
projects, or qualifications that are not mentioned in the profile.

If the requested information is not available, say:
"I don't have that information about Alanoud."

Keep your answers clear, friendly, and professional.

Alanoud's profile:
{profile}
"""

app = FastAPI()

# Allow Framer/frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Alanoud AI Assistant is running!"}


@app.post("/chat")
def chat(data: Question):

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": instructions
                },
                {
                    "role": "user",
                    "content": data.question
                }
            ],
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer
        }

    except Exception:
        return {
            "answer": "Sorry, I couldn't answer right now."
        }