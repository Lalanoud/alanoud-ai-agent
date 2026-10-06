from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv(Path(__file__).parent / ".env")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-120b"

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

If the requested information is not available, say:
"I don't have that information about Alanoud."

Keep your answers clear, friendly, and professional.

Alanoud's profile:
{profile}
"""

app = FastAPI()

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
                {"role": "system", "content": instructions},
                {"role": "user", "content": data.question}
            ],
        )

        return {
            "answer": response.choices[0].message.content
        }

    except Exception as error:
        # Log the real error server-side so it can be debugged
        print("Chat error:", error)
        return {
            "answer": "Sorry, I couldn't answer right now."
        }


# Raw string so backslashes inside the JS/CSS are never interpreted by Python
CHAT_UI_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Alanoud AI</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>

/* ------------------------------------------------------------------
   THEME — change the colors here to match the portfolio.
   Everything below uses these variables only.
------------------------------------------------------------------- */
:root {
    --bg:          #ffffff;   /* chat background */
    --surface:     #f5f5f3;   /* AI bubbles, chips, input */
    --ink:         #141414;   /* main text */
    --muted:       #7a7a76;   /* secondary text */
    --line:        #e8e8e5;   /* borders */
    --accent:      #141414;   /* header avatar, user bubble, send button */
    --accent-ink:  #ffffff;   /* text on top of accent */
    --online:      #3ba55d;   /* status dot */

    --radius-lg:   22px;
    --radius-md:   16px;
}

* {
    box-sizing: border-box;
}

html, body {
    height: 100%;
}

body {
    margin: 0;
    background: transparent;
    color: var(--ink);
    font-family: "Inter", -apple-system, BlinkMacSystemFont,
                 "Segoe UI", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}


/* CHAT WINDOW — fills the iframe it is embedded in */

#chat-window {
    width: 100%;
    height: 100%;
    max-width: 440px;
    max-height: 640px;
    margin: 0 auto;

    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.10);

    display: flex;
    flex-direction: column;
    overflow: hidden;
}


/* HEADER */

#header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: var(--bg);
    border-bottom: 1px solid var(--line);
}

#avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--accent);
    color: var(--accent-ink);
    display: grid;
    place-items: center;
    font-weight: 600;
    font-size: 16px;
    flex-shrink: 0;
}

#header-title {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.01em;
}

#header-subtitle {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 2px;
    font-size: 12px;
    color: var(--muted);
}

#status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--online);
}


/* MESSAGES */

#messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    scroll-behavior: smooth;
}

#messages::-webkit-scrollbar {
    width: 6px;
}

#messages::-webkit-scrollbar-thumb {
    background: var(--line);
    border-radius: 6px;
}

.message {
    max-width: 84%;
    padding: 11px 15px;
    border-radius: var(--radius-md);
    font-size: 14px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-wrap: break-word;
    animation: appear .25s ease;
}

.ai {
    align-self: flex-start;
    background: var(--surface);
    color: var(--ink);
    border-bottom-left-radius: 5px;
}

.user {
    align-self: flex-end;
    background: var(--accent);
    color: var(--accent-ink);
    border-bottom-right-radius: 5px;
}

@keyframes appear {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}


/* TYPING INDICATOR */

.typing {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 14px 16px;
}

.typing span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--muted);
    animation: bounce 1.2s infinite ease-in-out;
}

.typing span:nth-child(2) { animation-delay: .15s; }
.typing span:nth-child(3) { animation-delay: .30s; }

@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0);    opacity: .4; }
    30%           { transform: translateY(-4px); opacity: 1;  }
}


/* SUGGESTION CHIPS */

#suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 4px;
}

.chip {
    border: 1px solid var(--line);
    background: var(--bg);
    color: var(--ink);
    font: inherit;
    font-size: 13px;
    padding: 8px 13px;
    border-radius: 999px;
    cursor: pointer;
    transition: background .15s ease, border-color .15s ease;
}

.chip:hover {
    background: var(--surface);
    border-color: var(--ink);
}


/* INPUT */

#input-area {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 14px 16px 10px;
    background: var(--bg);
}

#question {
    flex: 1;
    height: 46px;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink);
    border-radius: 999px;
    padding: 0 18px;
    font: inherit;
    font-size: 14px;
    outline: none;
    transition: border-color .15s ease, background .15s ease;
}

#question::placeholder {
    color: var(--muted);
}

#question:focus {
    border-color: var(--ink);
    background: var(--bg);
}

#send {
    width: 46px;
    height: 46px;
    border: none;
    border-radius: 50%;
    background: var(--accent);
    color: var(--accent-ink);
    cursor: pointer;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    transition: transform .15s ease, opacity .15s ease;
}

#send:hover:not(:disabled) {
    transform: scale(1.05);
}

#send:disabled {
    opacity: .4;
    cursor: not-allowed;
}

#send svg {
    width: 18px;
    height: 18px;
}

#footer-note {
    text-align: center;
    font-size: 11px;
    color: var(--muted);
    padding: 0 16px 12px;
}


/* MOBILE */

@media (max-width: 450px) {
    #chat-window {
        max-width: none;
        max-height: none;
        border: none;
        border-radius: 0;
        box-shadow: none;
    }
}

</style>
</head>


<body>

<div id="chat-window">

    <div id="header">
        <div id="avatar">A</div>
        <div>
            <div id="header-title">Alanoud AI</div>
            <div id="header-subtitle">
                <span id="status-dot"></span>
                Ask me anything about Alanoud
            </div>
        </div>
    </div>

    <div id="messages">

        <div class="message ai">Hi! 👋 I'm Alanoud's AI assistant. Ask me about her education, skills, experience, or projects.</div>

        <div id="suggestions">
            <button class="chip" data-q="What is Alanoud's educational background?">Education</button>
            <button class="chip" data-q="What skills does Alanoud have?">Skills</button>
            <button class="chip" data-q="Tell me about Alanoud's projects.">Projects</button>
            <button class="chip" data-q="What work experience does Alanoud have?">Experience</button>
        </div>

    </div>

    <div id="input-area">
        <input
            id="question"
            type="text"
            dir="auto"
            placeholder="Ask about Alanoud..."
            autocomplete="off"
        >
        <button id="send" aria-label="Send message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 19V5"></path>
                <path d="M5 12l7-7 7 7"></path>
            </svg>
        </button>
    </div>

    <div id="footer-note">AI-generated answers based on Alanoud's profile</div>

</div>


<script>

const input       = document.getElementById("question");
const sendBtn     = document.getElementById("send");
const messages    = document.getElementById("messages");
const suggestions = document.getElementById("suggestions");

let busy = false;


function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
}


function addMessage(text, who) {
    const el = document.createElement("div");
    el.className = "message " + who;
    el.dir = "auto";              // supports Arabic (RTL) and English (LTR)
    el.textContent = text;
    messages.appendChild(el);
    scrollToBottom();
    return el;
}


function addTyping() {
    const el = document.createElement("div");
    el.className = "message ai typing";
    el.innerHTML = "<span></span><span></span><span></span>";
    messages.appendChild(el);
    scrollToBottom();
    return el;
}


function setBusy(state) {
    busy = state;
    sendBtn.disabled = state;
    input.disabled = state;
    if (!state) input.focus();
}


async function askAgent(presetQuestion) {

    const question = (presetQuestion || input.value).trim();

    if (!question || busy) return;

    // Hide the suggestion chips after the first question
    if (suggestions) suggestions.remove();

    addMessage(question, "user");
    input.value = "";
    setBusy(true);

    const typing = addTyping();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });

        if (!response.ok) throw new Error("Bad response");

        const data = await response.json();

        typing.remove();
        addMessage(data.answer, "ai");

    } catch (error) {

        typing.remove();
        addMessage("Sorry, I couldn't connect to the AI assistant.", "ai");

    } finally {

        setBusy(false);
    }
}


sendBtn.addEventListener("click", function () {
    askAgent();
});

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.isComposing) {
        askAgent();
    }
});

document.querySelectorAll(".chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
        askAgent(chip.dataset.q);
    });
});

</script>

</body>
</html>
"""


@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui():
    return CHAT_UI_HTML
