from flask import Flask, request, jsonify
from ai import generate_sql, format_answer
from database import run_query
import pandas as pd
import os

app = Flask(__name__)

def process_question(user_question):
    try:
        # Step 1 — Generate SQL
        sql = generate_sql(user_question)
        
        # Step 2 — Run SQL on DB
        columns, rows = run_query(sql)
        
        if isinstance(rows, str):
            return "Sorry, I could not fetch data. Please rephrase your question."
        
        df = pd.DataFrame(rows)
        
        # Step 3 — Format Answer
        answer = format_answer(
            user_question,
            sql,
            df.to_string() if df is not None else "No data"
        )
        
        return answer
    
    except Exception as e:
        return "Sorry, something went wrong. Please try again."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # GET — for webhook verification by ChatMitra
    if request.method == "GET":
        return jsonify({"status": "webhook active"}), 200
    
    # POST — incoming WhatsApp message
    if request.method == "POST":
        data = request.json
        
        # Extract message from ChatMitra payload
        try:
            user_message = data.get("message", "")
            sender = data.get("sender", "")
            
            if not user_message:
                return jsonify({"reply": "Please ask a question."}), 200
            
            # Process question
            answer = process_question(user_message)
            
            # Return answer to ChatMitra
            return jsonify({"reply": answer}), 200
        
        except Exception as e:
            return jsonify({"reply": "Sorry, something went wrong."}), 200

@app.route("/", methods=["GET"])
def home():
    return "Mor Sangwari Webhook is Live ✅", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)