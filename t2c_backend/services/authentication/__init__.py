import base64
import hashlib
import os
from urllib.parse import urljoin


class Authentication:
    _model = None

    def __init__(self, app) -> None:
        self.app = app

    @staticmethod
    def verify_hash(password: str, saved_salt: str) -> str:
        # Decode the Base64 encoded salt into bytes
        salt_bytes = base64.b64decode(saved_salt.encode("utf-8"))

        # Generate the key using the password and salt
        key = hashlib.pbkdf2_hmac(
            "sha256",  # HMAC digest algorithm
            password.encode("utf-8"),  # Convert password to bytes
            salt_bytes,  # Salt in bytes
            100000,  # SHA-256 iteration count
        )

        # Return Base64 encoded key
        return base64.b64encode(key).decode("utf-8")

    @staticmethod
    def generate_encoded_password(password: str) -> tuple[str, str]:
        # Generate a 32-byte salt
        salt = os.urandom(32)

        # Generate the key using the password and salt
        key = hashlib.pbkdf2_hmac(
            "sha256",  # HMAC digest algorithm
            password.encode("utf-8"),  # Convert password to bytes
            salt,  # Randomly generated salt
            100000,  # SHA-256 iteration count
        )

        # Return Base64 encoded salt and key as strings
        encoded_salt = base64.b64encode(salt).decode("utf-8")
        encoded_key = base64.b64encode(key).decode("utf-8")

        return encoded_salt, encoded_key

    def create_link_for_user_email_verification(self, token: str):
        return urljoin(str(self.app.config.FRONTEND_URL), f"/email-verification/?token={token}")

    def create_link_for_forgot_password_email_verification(self, token: str):
        return urljoin(str(self.app.config.FRONTEND_URL), f"/forgot-password/?token={token}")


def setup(app, session, *args, **kwargs):
    return app.add_service(Authentication(app), session.info["session_id"])
