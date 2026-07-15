import uuid

from pydantic import BaseModel


class GenerateFAQRequest(BaseModel):
    document_id: uuid.UUID


class FAQItem(BaseModel):
    question: str
    answer: str


class GenerateFAQResponse(BaseModel):
    document_title: str
    faqs: list[FAQItem]