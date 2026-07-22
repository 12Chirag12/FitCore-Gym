import json
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = "fitcore_secret_key"

# Email Configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER") or "info@fitcoregym.com"
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASS") or ""
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/trainers")
def trainers():
    return render_template("trainers.html")


def save_submission_locally(data):
    file_path = os.getenv("CONTACT_SUBMISSIONS_FILE", "contact_submissions.jsonl")
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **data,
    }

    with open(file_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


@app.route("/contact", methods=["POST"])
def contact():

    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    phone = request.form.get("phone")
    message = request.form.get("message")
    recipient = os.getenv("EMAIL_TO") or app.config["MAIL_USERNAME"]

    payload = {
        "name": name,
        "email": email,
        "phone": phone or "Not provided",
        "subject": subject,
        "message": message,
    }

    msg = Message(
        subject=f"FitCore Contact: {subject}",
        sender=app.config["MAIL_USERNAME"],
        recipients=[recipient],
    )

    msg.body = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone or 'Not provided'}
Subject: {subject}

Message:
{message}
"""

    try:
        if os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASS"):
            mail.send(msg)
            flash("Message sent successfully!", "success")
        else:
            save_submission_locally(payload)
            flash("Message saved locally. Configure email settings to receive it by email.", "info")

    except Exception as e:
        print(e)
        save_submission_locally(payload)
        flash("Your message was saved locally. We will follow up soon.", "warning")

    return redirect("/")


if __name__ == "__main__":
    app.run()