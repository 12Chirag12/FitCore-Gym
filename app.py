import json
import os
from datetime import datetime

import traceback

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_from_directory
from flask_mail import Mail, Message

project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, ".env"))

app = Flask(__name__)
app.secret_key = "fitcore_secret_key"

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME") or os.getenv("EMAIL_USER") or ""
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD") or os.getenv("EMAIL_PASS") or ""
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail()


def configure_mail_from_environment():
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", app.config.get("MAIL_SERVER", "smtp.gmail.com"))
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", app.config.get("MAIL_PORT", 587)))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", str(app.config.get("MAIL_USE_TLS", True))).lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME") or os.getenv("EMAIL_USER") or ""
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD") or os.getenv("EMAIL_PASS") or ""
    app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]
    mail.init_app(app)


configure_mail_from_environment()


def email_configured():
    username = app.config.get("MAIL_USERNAME", "")
    password = app.config.get("MAIL_PASSWORD", "")
    return bool(username and password)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/trainers")
def trainers():
    return render_template("trainers.html")


def save_submission_locally(data):
    file_path = os.getenv("CONTACT_SUBMISSIONS_FILE", os.path.join(project_root, "contact_submissions.jsonl"))
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **data,
    }

    try:
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
        return True
    except OSError as exc:
        print(f"Could not save contact submission locally: {exc}")
        return False


@app.route("/contact", methods=["POST"])
def contact():
    payload = {
        "name": None,
        "email": None,
        "phone": "Not provided",
        "subject": None,
        "message": None,
    }

    try:
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        phone = request.form.get("phone")
        message = request.form.get("message")

        configure_mail_from_environment()

        payload = {
            "name": name,
            "email": email,
            "phone": phone or "Not provided",
            "subject": subject,
            "message": message,
        }

        if not email_configured():
            save_submission_locally(payload)
            flash("Message saved locally. Configure email settings to receive it by email.", "info")
            return redirect("/")

        recipient = os.getenv("EMAIL_TO") or app.config.get("MAIL_USERNAME") or ""
        if not recipient:
            save_submission_locally(payload)
            flash("Message saved locally. Configure email settings to receive it by email.", "info")
            return redirect("/")

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

        mail.send(msg)
        flash("Message sent successfully!", "success")
    except (Exception, SystemExit) as exc:
        print(f"Contact form email send failed: {exc}")
        traceback.print_exc()
        save_submission_locally(payload)
        flash("Your message was saved locally. We will follow up soon.", "warning")

    return redirect("/")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static", "images", "logo"), "favicon.png", mimetype="image/png")


if __name__ == "__main__":
    app.run()