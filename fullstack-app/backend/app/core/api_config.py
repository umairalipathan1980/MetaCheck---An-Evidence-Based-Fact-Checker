"""
Shared API configuration for OpenAI.

This module provides reusable configuration utilities for creating
OpenAI clients across different modules.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from backend/.env explicitly
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def _g(name: str, default: str | None = None) -> str | None:
    """Get env var trimmed of whitespace."""
    val = os.getenv(name, default)
    if isinstance(val, str):
        val = val.strip()
    return val


def get_openai_config() -> dict:
    """Get OpenAI configuration (standard OpenAI only)."""
    return {
        'api_key': _g("OPENAI_API_KEY"),
        'model': _g("OPENAI_MODEL", "gpt-4.1"),
        'transcription_model': _g("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"),
    }


def create_openai_client(config: dict):
    """Create a standard OpenAI client."""
    return OpenAI(api_key=config['api_key'])
