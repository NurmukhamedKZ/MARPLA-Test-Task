from pydantic import BaseModel, Field


class SEORequest(BaseModel):
    product_name: str
    category: str
    keywords: list[str]


class SEOResponse(BaseModel):
    title: str = Field(description="SEO title tag, 50–60 chars")
    meta_description: str = Field(description="Meta description, 150–160 chars")
    h1: str = Field(description="Main page heading")
    description: str = Field(description="Product description, 2–3 paragraphs")
    bullets: list[str] = Field(description="Key feature bullet points, 4–6 items")
