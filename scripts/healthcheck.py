#!/usr/bin/env python3
"""Check the public frontend and its backend proxy without contacting an LLM."""

import requests


def healthy():
    try:
        response = requests.get(
            "http://127.0.0.1:8080/api/health", timeout=3, allow_redirects=False
        )
        try:
            if response.status_code != 200:
                return False
            payload = response.json()
            return isinstance(payload, dict) and payload.get("status") == "ok"
        finally:
            response.close()
    except (requests.RequestException, ValueError):
        return False


if __name__ == "__main__":
    raise SystemExit(0 if healthy() else 1)
