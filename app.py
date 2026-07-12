from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

print("EMAIL_USER =", os.getenv("EMAIL_USER"))
print("EMAIL_PASS =", os.getenv("EMAIL_PASS"))

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = "fitcore_secret_key"

# Email Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASS")

mail = Mail(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():

    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    msg = Message(
        subject=f"FitCore Contact: {subject}",
        sender=app.config["MAIL_USERNAME"],
        recipients=[app.config["MAIL_USERNAME"]]
    )

    msg.body = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

    try:
        mail.send(msg)
        flash("Message sent successfully!", "success")

    except Exception as e:
        print(e)
        flash("Something went wrong. Please try again.", "danger")

    return redirect("/")


if __name__ == "__main__":
    app.run()