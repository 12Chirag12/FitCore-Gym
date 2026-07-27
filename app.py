import json
import os
from datetime import datetime

import traceback

import resend
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_from_directory

project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_root, ".env"))

app = Flask(__name__)
app.secret_key = "fitcore_secret_key"


def configure_resend_from_environment():
    resend.api_key = os.getenv("RESEND_API_KEY", "")


def get_resend_from_address():
    return (
        os.getenv("RESEND_FROM")
        or os.getenv("EMAIL_FROM")
        or os.getenv("MAIL_USERNAME")
        or os.getenv("EMAIL_USER")
        or ""
    )


def get_resend_from_display():
    address = get_resend_from_address()
    if not address:
        return ""
    if "<" in address and ">" in address:
        return address
    sender_name = os.getenv("RESEND_FROM_NAME", "FitCore Gym")
    return f"{sender_name} <{address}>"


configure_resend_from_environment()


def email_configured():
    return bool(os.getenv("RESEND_API_KEY") and get_resend_from_address())


def send_contact_email(name, email, phone, subject, message, recipient):
    body = f"""New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone or 'Not provided'}
Subject: {subject}

Message:
{message}
"""
    html_body = f"""<p><strong>New Contact Form Submission</strong></p>
<ul>
  <li><strong>Name:</strong> {name}</li>
  <li><strong>Email:</strong> {email}</li>
  <li><strong>Phone:</strong> {phone or 'Not provided'}</li>
  <li><strong>Subject:</strong> {subject}</li>
</ul>
<p><strong>Message:</strong></p>
<p>{message.replace(chr(10), '<br>')}</p>"""

    params: resend.Emails.SendParams = {
        "from": get_resend_from_display(),
        "to": [recipient],
        "reply_to": email,
        "subject": f"FitCore Contact: {subject}",
        "text": body,
        "html": html_body,
    }

    print(
        "Attempting Resend send",
        {
            "from": get_resend_from_display(),
            "recipient": recipient,
            "reply_to": email,
        },
    )
    return resend.Emails.send(params)


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

        configure_resend_from_environment()

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

        recipient = os.getenv("EMAIL_TO") or get_resend_from_address()
        if not recipient:
            save_submission_locally(payload)
            flash("Message saved locally. Configure email settings to receive it by email.", "info")
            return redirect("/")

        send_contact_email(name, email, phone, subject, message, recipient)
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
