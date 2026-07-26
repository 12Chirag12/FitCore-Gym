import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as app_module
from app import app as flask_app


class ContactFlowTests(unittest.TestCase):
    def setUp(self):
        flask_app.config.update(TESTING=True)
        self.client = flask_app.test_client()
        self.original_email_user = os.environ.get("EMAIL_USER")
        self.original_email_pass = os.environ.get("EMAIL_PASS")
        self.original_email_to = os.environ.get("EMAIL_TO")
        self.original_mail_username = os.environ.get("MAIL_USERNAME")
        self.original_mail_password = os.environ.get("MAIL_PASSWORD")

        os.environ.pop("EMAIL_USER", None)
        os.environ.pop("EMAIL_PASS", None)
        os.environ.pop("EMAIL_TO", None)
        os.environ.pop("MAIL_USERNAME", None)
        os.environ.pop("MAIL_PASSWORD", None)

        self.temp_dir = tempfile.mkdtemp(dir=os.getcwd())
        self.original_upload_dir = os.environ.get("CONTACT_SUBMISSIONS_FILE")
        os.environ["CONTACT_SUBMISSIONS_FILE"] = os.path.join(self.temp_dir, "submissions.jsonl")

        if os.path.exists(os.environ["CONTACT_SUBMISSIONS_FILE"]):
            os.remove(os.environ["CONTACT_SUBMISSIONS_FILE"])

    def tearDown(self):
        if self.original_email_user is None:
            os.environ.pop("EMAIL_USER", None)
        else:
            os.environ["EMAIL_USER"] = self.original_email_user

        if self.original_email_pass is None:
            os.environ.pop("EMAIL_PASS", None)
        else:
            os.environ["EMAIL_PASS"] = self.original_email_pass

        if self.original_email_to is None:
            os.environ.pop("EMAIL_TO", None)
        else:
            os.environ["EMAIL_TO"] = self.original_email_to

        if self.original_mail_username is None:
            os.environ.pop("MAIL_USERNAME", None)
        else:
            os.environ["MAIL_USERNAME"] = self.original_mail_username

        if self.original_mail_password is None:
            os.environ.pop("MAIL_PASSWORD", None)
        else:
            os.environ["MAIL_PASSWORD"] = self.original_mail_password

        if self.original_upload_dir is None:
            os.environ.pop("CONTACT_SUBMISSIONS_FILE", None)
        else:
            os.environ["CONTACT_SUBMISSIONS_FILE"] = self.original_upload_dir

        for file_name in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file_name))
        os.rmdir(self.temp_dir)

    def test_contact_form_falls_back_to_local_storage_when_email_not_configured(self):
        response = self.client.post(
            "/contact",
            data={
                "name": "Asha",
                "email": "asha@example.com",
                "subject": "Trial Request",
                "phone": "9876543210",
                "message": "I want to book a free trial.",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("saved locally", response.get_data(as_text=True).lower())

        submissions_file = os.environ["CONTACT_SUBMISSIONS_FILE"]
        self.assertTrue(os.path.exists(submissions_file))

        with open(submissions_file, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("asha@example.com", content)

    def test_contact_form_uses_render_email_environment_variables(self):
        os.environ["MAIL_USERNAME"] = "info@fitcoregym.com"
        os.environ["MAIL_PASSWORD"] = "secret-password"

        with patch.object(app_module.mail, "send", return_value=None) as mock_send:
            response = self.client.post(
                "/contact",
                data={
                    "name": "Asha",
                    "email": "asha@example.com",
                    "subject": "Trial Request",
                    "phone": "9876543210",
                    "message": "I want to book a free trial.",
                },
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("sent successfully", response.get_data(as_text=True).lower())
        mock_send.assert_called_once()

    def test_app_loads_dotenv_from_project_root_even_when_cwd_changes(self):
        original_cwd = os.getcwd()
        temp_dir = tempfile.mkdtemp(dir=os.getcwd())
        try:
            os.chdir(temp_dir)
            os.environ.pop("MAIL_USERNAME", None)
            os.environ.pop("MAIL_PASSWORD", None)
            os.environ.pop("EMAIL_USER", None)
            os.environ.pop("EMAIL_PASS", None)

            reloaded_app = importlib.reload(app_module)
            self.assertTrue(reloaded_app.email_configured())
            self.assertEqual(reloaded_app.app.config["MAIL_USERNAME"], os.getenv("EMAIL_USER") or os.getenv("MAIL_USERNAME"))
        finally:
            os.chdir(original_cwd)
            for file_name in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file_name))
            os.rmdir(temp_dir)


if __name__ == "__main__":
    unittest.main()
