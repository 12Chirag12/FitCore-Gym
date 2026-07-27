import importlib
import os
import tempfile
import unittest
from unittest.mock import patch

import app as app_module
from app import app as flask_app


class ContactFlowTests(unittest.TestCase):
    def setUp(self):
        flask_app.config.update(TESTING=True)
        self.client = flask_app.test_client()
        self.original_resend_api_key = os.environ.get("RESEND_API_KEY")
        self.original_resend_from = os.environ.get("RESEND_FROM")
        self.original_email_from = os.environ.get("EMAIL_FROM")
        self.original_email_to = os.environ.get("EMAIL_TO")
        self.original_mail_username = os.environ.get("MAIL_USERNAME")
        self.original_email_user = os.environ.get("EMAIL_USER")

        os.environ.pop("RESEND_API_KEY", None)
        os.environ.pop("RESEND_FROM", None)
        os.environ.pop("EMAIL_FROM", None)
        os.environ.pop("EMAIL_TO", None)
        os.environ.pop("MAIL_USERNAME", None)
        os.environ.pop("EMAIL_USER", None)

        self.temp_dir = tempfile.mkdtemp(dir=os.getcwd())
        self.original_upload_dir = os.environ.get("CONTACT_SUBMISSIONS_FILE")
        os.environ["CONTACT_SUBMISSIONS_FILE"] = os.path.join(self.temp_dir, "submissions.jsonl")

        if os.path.exists(os.environ["CONTACT_SUBMISSIONS_FILE"]):
            os.remove(os.environ["CONTACT_SUBMISSIONS_FILE"])

    def tearDown(self):
        env_pairs = [
            ("RESEND_API_KEY", self.original_resend_api_key),
            ("RESEND_FROM", self.original_resend_from),
            ("EMAIL_FROM", self.original_email_from),
            ("EMAIL_TO", self.original_email_to),
            ("MAIL_USERNAME", self.original_mail_username),
            ("EMAIL_USER", self.original_email_user),
        ]

        for key, original_value in env_pairs:
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

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

    def test_contact_form_sends_email_with_resend(self):
        os.environ["RESEND_API_KEY"] = "re_test_key"
        os.environ["RESEND_FROM"] = "info@fitcoregym.com"

        with patch.object(app_module.resend.Emails, "send", return_value={"id": "email_123"}) as mock_send:
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

    def test_contact_form_falls_back_to_local_storage_when_resend_send_fails(self):
        os.environ["RESEND_API_KEY"] = "re_test_key"
        os.environ["RESEND_FROM"] = "info@fitcoregym.com"

        with patch.object(app_module.resend.Emails, "send", side_effect=SystemExit(1)):
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

    def test_app_loads_dotenv_from_project_root_even_when_cwd_changes(self):
        original_cwd = os.getcwd()
        temp_dir = tempfile.mkdtemp(dir=os.getcwd())
        try:
            os.chdir(temp_dir)
            os.environ.pop("RESEND_API_KEY", None)
            os.environ.pop("RESEND_FROM", None)
            os.environ.pop("EMAIL_FROM", None)
            os.environ.pop("MAIL_USERNAME", None)
            os.environ.pop("EMAIL_USER", None)

            reloaded_app = importlib.reload(app_module)
            expected_from = (
                os.getenv("RESEND_FROM")
                or os.getenv("EMAIL_FROM")
                or os.getenv("EMAIL_USER")
                or os.getenv("MAIL_USERNAME")
            )

            if not os.getenv("RESEND_API_KEY") or not expected_from:
                self.skipTest("Set RESEND_API_KEY and a sender address in .env to run this test.")

            self.assertTrue(reloaded_app.email_configured())
            self.assertEqual(reloaded_app.get_resend_from_address(), expected_from)
        finally:
            os.chdir(original_cwd)
            for file_name in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file_name))
            os.rmdir(temp_dir)


if __name__ == "__main__":
    unittest.main()
