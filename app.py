from flask import Flask, request, render_template, jsonify
import pandas as pd
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

app = Flask(__name__)

# Load Excel data once
workers = pd.read_excel('students.xlsx')

# DB setup
conn = sqlite3.connect('complaint_log.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs (
    name TEXT,
    id TEXT,
    timestamp TEXT
)''')
conn.commit()

# Helper: Count complaints in past 24 hours
def recent_complaint_count(name, id):
    cutoff = datetime.utcnow() - timedelta(days=1)
    c.execute("SELECT COUNT(*) FROM logs WHERE name=? AND id=? AND timestamp >= ?", 
              (name, id, cutoff.isoformat()))
    return c.fetchone()[0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get("query", "").strip().lower()
    matches = workers[workers.apply(lambda row: query in str(row['Name']).lower() or query in str(row['ID']), axis=1)]
    return matches[['Name', 'ID']].to_dict(orient='records')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    name = data['name']
    id = data['id']
    message = data['message']

    if recent_complaint_count(name, id) >= 3:
        return jsonify({"status": "error", "message": "Complaint limit reached for today"}), 429

    # Send email
    email = EmailMessage()
    email.set_content(message)
    email['Subject'] = f"Complaint from {name} - ID: {id}"
    email['From'] = "mailforwarding619@gmail.com"  # Use your email @Mailforwardingpassword1900
    email['To'] = "tedecia.powellcoley_r6@moeschools.edu.jm"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("mailforwarding619@gmail.com", "cgra tzjg qdgu cubn ")  # Use App Password
            smtp.send_message(email)

        # Log complaint
        c.execute("INSERT INTO logs VALUES (?, ?, ?)", (name, id, datetime.utcnow().isoformat()))
        conn.commit()
        return jsonify({"status": "success", "message": "Complaint sent successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

