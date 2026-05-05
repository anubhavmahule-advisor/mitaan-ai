from flask import Flask, request, jsonify
from ai import generate_sql, format_answer
from database import run_query
import pandas as pd
import os
import time

# Creates the web server that listens for incoming WhatsApp messages
app = Flask(__name__)

# Greeting message shown when boss first messages
GREETING = """🙏 *Welcome to Mor Sangwari!*
_Your AI-powered Mitaan companion_
─────────────────────
I can help you with:
📊 Pending cases analysis
📍 ULB wise performance
🔄 Sent back cases
❌ Rejection analysis
📦 Delivery status
─────────────────────
Type *menu* anytime to see options
Or just ask your question directly!"""

# Menu shown when boss types menu
MENU = """📋 *Mor Sangwari Menu*
─────────────────────
Ask me anything like:

📌 *Pending Cases*
→ Total pending cases today?
→ Pending in Raipur this week?

↩️ *Sent Back*
→ Sent backs yesterday?
→ Sent backs in Raipur and Balod?

❌ *Rejections*
→ Total rejections this week?
→ Which service rejected most?

✅ *Completed*
→ Completed cases today?
→ Completion rate this month?

📍 *ULB Analysis*
→ Top 5 ULBs pending cases?
→ Worst performing ULB?

💡 _You can also ask in Hinglish!_
→ Raipur mein kitne pending hain?"""

def process_question(user_question):
    # Main function that converts question to SQL, runs it and formats answer
    try:
        # Retry up to 3 times if Gemini is busy
        for attempt in range(3):
            try:
                sql = generate_sql(user_question)
                print(f"Generated SQL: {sql}")
                break
            except Exception as e:
                print(f"Gemini attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(3)
                else:
                    raise

        # Run SQL on Mitaan DB
        columns, rows = run_query(sql)
        print(f"DB rows fetched: {len(rows) if not isinstance(rows, str) else rows}")

        if isinstance(rows, str):
            return f"❌ Could not fetch data.\nPlease rephrase your question."

        df = pd.DataFrame(rows)

        # Format answer in WhatsApp style
        answer = format_answer(
            user_question,
            sql,
            df.to_string() if df is not None else "No data"
        )
        return answer

    except Exception as e:
        print(f"Error in process_question: {str(e)}")
        return "❌ Something went wrong. Please try again."

def extract_message(data):
    # Try multiple possible ChatMitra payload formats to extract message text
    print(f"FULL PAYLOAD RECEIVED: {data}")

    # Format 1 — simple flat format
    if isinstance(data.get("message"), str):
        return data.get("message", "").strip(), data.get("sender", "")

    # Format 2 — nested message object
    if data.get("data"):
        inner = data.get("data", {})
        message_obj = inner.get("message", {})
        contact_obj = inner.get("contact", {})

        text = message_obj.get("text", "") if isinstance(message_obj, dict) else ""
        sender = contact_obj.get("phone", "") if isinstance(contact_obj, dict) else ""
        if text:
            return text.strip(), sender

    # Format 3 — messages array
    if data.get("messages"):
        messages = data.get("messages", [])
        if len(messages) > 0:
            msg = messages[0]
            text = msg.get("text", {}).get("body", "")
            sender = msg.get("from", "")
            if text:
                return text.strip(), sender

    # Format 4 — entry array (Meta standard format)
    if data.get("entry"):
        try:
            entry = data["entry"][0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [{}])
            if messages:
                text = messages[0].get("text", {}).get("body", "")
                sender = messages[0].get("from", "")
                if text:
                    return text.strip(), sender
        except Exception as e:
            print(f"Format 4 extraction error: {str(e)}")

    # Nothing matched
    print("Could not extract message from payload")
    return "", ""

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # GET request — for webhook verification
    if request.method == "GET":
        return jsonify({"status": "webhook active"}), 200

    # POST request — incoming WhatsApp message
    if request.method == "POST":
        data = request.json
        print(f"RAW DATA: {data}")

        try:
            # Extract message using multiple format attempts
            user_message, sender = extract_message(data)
            print(f"Extracted message: '{user_message}' from sender: '{sender}'")

            if not user_message:
                return jsonify({"reply": "Please ask a question."}), 200

            # Show greeting for hi/hello
            if user_message.lower() in ["hi", "hello", "hey", "namaste", "hii"]:
                return jsonify({"reply": GREETING}), 200

            # Show menu
            if user_message.lower() == "menu":
                return jsonify({"reply": MENU}), 200

            # Process actual question
            answer = process_question(user_message)
            return jsonify({"reply": answer}), 200

        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return jsonify({"reply": "❌ Something went wrong. Please try again."}), 200

@app.route("/", methods=["GET"])
def home():
    return "Mor Sangwari Webhook is Live ✅", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)