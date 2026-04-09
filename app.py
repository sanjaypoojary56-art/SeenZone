import json
from flask import Flask, render_template, request
from google import genai
import os

app = Flask(__name__)

# 🔑 Set your API key
client = genai.Client(api_key=os.getenv("API_KEY"))

# 🔥 AI decode function
def ai_decode(msg):
    prompt = f"""
    You are an expert at interpreting short messages in relationships.
    it must like not overthinking only simple to make a overthinker to think like normal

    Message: "{msg}"

    Return ONLY JSON:
    {{
      "meaning": "",
      "tone": "",
      "risk": ""
    }}
    Keep answers short.means for mening asentence and then for other two one one words
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Clean markdown if present
        if text.startswith("```"):
            text = text.split("```")[1]
            text = text.replace("json", "").strip()

        data = json.loads(text)

        return (
            data.get("meaning", "Unknown"),
            data.get("tone", "Unknown"),
            data.get("risk", "Unknown")
        )

    except Exception as e:
        print("AI Error:", e)
        return ("Could not analyze message", "Unknown", "Low")


# 🔥 Rule-based first
def decode_message(msg):
    msg_lower = msg.lower()

    if "busy" in msg_lower:
        return ("Actually busy. Don’t overthink.", "Neutral", "Low")

    elif "feeling free" in msg_lower:
        return ("She is watching Movei on Netflix so Feeling Free", "Natural", "Low")

    elif msg_lower.strip() in ["k", "ok"]:
        return ("Short reply. Possibly annoyed or neutral.", "Unclear", "Medium")

    elif "meet me tomorrow" in msg_lower:
        return ("Attendance Shortage ☠, Pray Bro 🛕", "Danger", "High")

    elif "call me urgent" in msg:
        return ("He Needs Money", "Uncertain", "High")
    elif "we need to talk tomorrow" in msg_lower:
        return ("Now real problem🥶,Started", "Danger☠️", "High")
    else:
        return ai_decode(msg)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        message = request.form.get("message")

        meaning, tone, risk = decode_message(message)

        result = {
            "message": message,
            "meaning": meaning,
            "tone": tone,
            "risk": risk
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
    
