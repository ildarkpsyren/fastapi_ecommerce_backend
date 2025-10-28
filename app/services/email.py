"""Utility helpers for email related tasks."""

def send_verification_email(email: str, token: str) -> None:
    """Placeholder implementation for sending verification emails."""

    # In a real-world project this function would integrate with an email
    # provider. The placeholder makes the flow explicit for future work while
    # keeping the current project self-contained.
    print(f"[EMAIL] Send verification token {token} to {email}")
