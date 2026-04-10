import json
import os
from flask import Flask, render_template, request
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("API_KEY"))


# 🔥 Fallback (never fails)
def fallback_logic(msg):
    msg_lower = msg.lower()

    if msg_lower in ["k", "ok"]:
        return ("Short reply, likely neutral.", "Neutral", "Low")

    elif "busy" in msg_lower:
        return ("They are busy, nothing serious.", "Neutral", "Low")

    return ("Simple message, nothing serious.", "Neutral", "Low")


# 🔥 AI Decode (robust)
def ai_decode(msg):
    prompt = f"""
Return STRICT JSON only.

Format:
{{"meaning":"...","tone":"...","risk":"..."}}

Rules:
- Meaning: one short sentence
- Tone: one word
- Risk: one word

Message: "{msg}"
"""

    for _ in range(2):  # retry 2 times
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()

            # Clean markdown
            text = text.replace("```json", "").replace("```", "").strip()

            # Extract JSON safely
            start = text.find("{")
            end = text.rfind("}") + 1
            json_text = text[start:end]

            data = json.loads(json_text)

            return (
                data.get("meaning", "Unknown"),
                data.get("tone", "Unknown"),
                data.get("risk", "Low")
            )

        except Exception as e:
            print("Retrying AI...", e)

    # Final fallback
    return fallback_logic(msg)


# 🔥 Rule-based first (fast + reliable)
def decode_message(msg):
    msg_lower = msg.lower().strip()

    if "busy" in msg_lower:
        return ("Actually busy. Don't overthink.", "Neutral", "Low")

    elif msg_lower in ["k", "ok"]:
        return ("Short reply. Possibly neutral.", "Unclear", "Medium")

    elif "meet me tomorrow" in msg_lower:
        return ("Something important coming.", "Serious", "High")

    elif "call me urgent" in msg_lower:
        return ("Needs immediate attention.", "Urgent", "High")

    elif "we need to talk tomorrow" in msg_lower:
        return ("Likely serious discussion.", "Serious", "High")

    else:
        return ai_decode(msg)


# 🔥 Route
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        message = request.form.get("message")

        if message:
            meaning, tone, risk = decode_message(message)

            result = {
                "message": message,
                "meaning": meaning,
                "tone": tone,
                "risk": risk
            }

    return render_template("index.html", result=result)


# 🔥 Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)    
