import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models import SEOResponse

VALID_PAYLOAD = {
    "product_name": "Wireless Noise-Cancelling Headphones",
    "category": "Electronics",
    "keywords": ["noise cancelling", "wireless", "bluetooth headphones"],
}

VALID_SEO = SEOResponse(
    title="Best Wireless Noise-Cancelling Headphones 2024",
    meta_description="Shop top-rated wireless noise-cancelling headphones with 30h battery. Free shipping. Experience pure sound with Bluetooth 5.0.",
    h1="Wireless Noise-Cancelling Headphones",
    description="Immerse yourself in crystal-clear audio...\n\nPerfect for travel and work...",
    bullets=["Active noise cancellation", "30-hour battery life", "Bluetooth 5.0", "Foldable design"],
)


def _sse_data(response_text: str) -> list[dict]:
    """Parse SSE events from raw response text."""
    events = []
    for line in response_text.strip().splitlines():
        if line.startswith("data: ") and line != "data: [DONE]":
            events.append(json.loads(line[6:]))
    return events


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# --- happy path ---

def test_generate_seo_returns_structured_output(client):
    with patch("app.main.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=VALID_SEO)
        resp = client.post("/api/generate-seo", json=VALID_PAYLOAD)

    assert resp.status_code == 200
    events = _sse_data(resp.text)
    assert len(events) == 1
    data = events[0]
    assert data["title"] == VALID_SEO.title
    assert data["meta_description"] == VALID_SEO.meta_description
    assert isinstance(data["bullets"], list)


# --- edge cases ---

def test_timeout_returns_error_event(client):
    async def _slow(*_a, **_kw):
        await asyncio.sleep(999)

    with patch("app.main.chain") as mock_chain:
        mock_chain.ainvoke = _slow
        with patch("app.config.settings.request_timeout", 0):
            resp = client.post("/api/generate-seo", json=VALID_PAYLOAD)

    events = _sse_data(resp.text)
    assert any(e.get("error") == "timeout" for e in events)


def test_none_response_returns_invalid_response_error(client):
    with patch("app.main.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=None)
        resp = client.post("/api/generate-seo", json=VALID_PAYLOAD)

    events = _sse_data(resp.text)
    assert any(e.get("error") == "invalid_response" for e in events)


def test_llm_exception_returns_internal_error(client):
    with patch("app.main.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(side_effect=RuntimeError("model overloaded"))
        resp = client.post("/api/generate-seo", json=VALID_PAYLOAD)

    events = _sse_data(resp.text)
    assert any(e.get("error") == "internal_error" for e in events)


def test_invalid_request_body_returns_422(client):
    resp = client.post("/api/generate-seo", json={"product_name": "X"})
    assert resp.status_code == 422


def test_done_sentinel_always_present(client):
    with patch("app.main.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=VALID_SEO)
        resp = client.post("/api/generate-seo", json=VALID_PAYLOAD)

    assert "data: [DONE]" in resp.text
