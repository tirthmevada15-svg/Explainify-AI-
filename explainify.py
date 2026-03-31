from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
from groq import Groq
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Explainify, a highly intelligent and friendly AI assistant.
You explain things clearly and concisely, just like ChatGPT.
You can answer questions on any topic — science, math, coding, history, creative writing, and more.
When writing code, always use proper markdown code blocks with language specified.
Be helpful, accurate, and conversational. Format responses with markdown when appropriate."""

client = Groq(api_key=API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        conversation.append({"role": msg["role"], "content": msg["content"]})

    def generate():
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=conversation,
                max_tokens=2048,
                temperature=0.7,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield f"data: {json.dumps({'text': delta})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)