import sqlite3

# Connect to database
conn = sqlite3.connect("chat_history.db")
cursor = conn.cursor()

cursor.execute("""
SELECT timestamp, user_input, bot_response 
FROM logs 
ORDER BY id DESC
""")

rows = cursor.fetchall()
conn.close()

# HTML content
html = """
<!DOCTYPE html>
<html>
<head>
    <title>CareConnect – Chat History</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            padding: 20px;
        }
        h1 {
            text-align: center;
        }
        .card {
            background: white;
            padding: 15px;
            margin: 15px auto;
            width: 80%;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }
        textarea {
            width: 100%;
            height: 70px;
            resize: none;
            padding: 8px;
        }
        .time {
            text-align: right;
            font-size: 0.9em;
            color: gray;
        }
    </style>
</head>
<body>

<h1>🩺 CareConnect – Chat Records</h1>
"""

# Add records
for row in rows:
    timestamp, user_input, bot_response = row
    html += f"""
    <div class="card">
        <div class="time">🕒 {timestamp}</div>

        <label>User Input</label>
        <textarea readonly>{user_input}</textarea>

        <label>Bot Response</label>
        <textarea readonly>{bot_response}</textarea>
    </div>
    """

html += """
</body>
</html>
"""

# Write to file
with open("chat_history_form.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ File created: chat_history_form.html")