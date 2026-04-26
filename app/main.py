import asyncio
import json
import logging

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from .chain import build_chain
from .config import settings
from .models import SEORequest, SEOResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="SEO Generator API")
chain = build_chain()


@app.post("/api/generate-seo")
async def generate_seo(body: SEORequest) -> StreamingResponse:
    async def _stream():
        try:
            result: SEOResponse = await asyncio.wait_for(
                chain.ainvoke({
                    "product_name": body.product_name,
                    "category": body.category,
                    "keywords": ", ".join(body.keywords),
                }),
                timeout=settings.request_timeout,
            )

            if result is None:
                raise ValueError("LLM returned an empty response")

            yield f"data: {result.model_dump_json()}\n\n"

        except asyncio.TimeoutError:
            logger.error("LLM request timed out after %ds", settings.request_timeout)
            yield _error_event("timeout", f"Request timed out after {settings.request_timeout}s")

        except (ValueError, ValidationError) as exc:
            logger.warning("Empty or unparseable LLM response: %s", exc)
            yield _error_event("invalid_response", str(exc))

        except Exception as exc:
            logger.exception("Unexpected error during SEO generation")
            yield _error_event("internal_error", str(exc))

        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(_stream(), media_type="text/event-stream")


def _error_event(code: str, detail: str) -> str:
    return f"data: {json.dumps({'error': code, 'detail': detail})}\n\n"
