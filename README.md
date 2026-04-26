# SEO Product Description Generator

A FastAPI service that generates structured, keyword-optimized SEO content for products using OpenAI via LangChain.

## What it does

Send a product name, category, and target keywords — get back a complete SEO content package streamed as Server-Sent Events:

- **Title tag** (50–60 chars)
- **Meta description** (150–160 chars)
- **H1 heading**
- **Product description** (2–3 paragraphs)
- **Feature bullets** (4–6 items)

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (package manager)
- OpenAI API key

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

## Running

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

## API

### `POST /api/generate-seo`

**Request body:**

```json
{
  "product_name": "Wireless Noise-Cancelling Headphones",
  "category": "Electronics",
  "keywords": ["noise cancelling", "wireless", "bluetooth headphones"]
}
```

**Response:** `text/event-stream`

Each SSE event is either a JSON payload on success or an error object:

```
data: {"title": "...", "meta_description": "...", "h1": "...", "description": "...", "bullets": [...]}

data: [DONE]
```

**Error event shape:**

```json
{ "error": "timeout" | "invalid_response" | "internal_error", "detail": "..." }
```

## Configuration

All settings are read from environment variables (or `.env`):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use |
| `TEMPERATURE` | `0.7` | Sampling temperature |
| `REQUEST_TIMEOUT` | `30` | LLM timeout in seconds |

## Testing

```bash
uv run pytest
```

Tests use mocked LangChain chains and cover the happy path, timeout, empty/invalid LLM responses, and malformed request bodies.
