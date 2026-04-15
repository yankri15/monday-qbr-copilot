"""Vercel Python entrypoint for the backend service."""

from app.factory import create_app

app = create_app(api_prefix="")
