from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from .config import settings
from .models import SEOResponse

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert SEO copywriter. "
        "Create compelling, keyword-optimized product content that drives conversions. "
        "Naturally weave provided keywords throughout.",
    ),
    (
        "human",
        "Generate SEO content for the following product:\n\n"
        "Product: {product_name}\n"
        "Category: {category}\n"
        "Target keywords: {keywords}\n\n"
        "Constraints: title 50–60 chars · meta 150–160 chars · 4–6 bullets",
    ),
])


def build_chain() -> Runnable:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
    )
    return _PROMPT | llm.with_structured_output(SEOResponse)
