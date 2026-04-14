"""Feature extraction stubs for phishing URL analysis."""

from typing import Dict


def extract_url_features(url: str) -> Dict[str, int]:
    """Return basic URL-level features. Replace with full logic."""
    return {
        "url_length": len(url),
        "has_https": 1 if url.startswith("https://") else 0
    }
