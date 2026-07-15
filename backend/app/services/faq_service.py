import re

from app.schemas.faq import FAQItem


def parse_faq_response(raw_text: str) -> list[FAQItem]:
    """Parse the LLM's numbered Q/A text output into structured FAQItem objects.

    Expects a format like:
        1. Q: What is X?
           A: X is...
        2. Q: What is Y?
           A: Y is...

    Falls back to treating the whole response as one unparsed item if the
    expected pattern isn't found, rather than raising an error.
    """
    pattern = re.compile(r"Q:\s*(.+?)\s*A:\s*(.+?)(?=(?:\d+[\.\)]\s*Q:)|\Z)", re.DOTALL)
    matches = pattern.findall(raw_text)

    if not matches:
        return [FAQItem(question="Generated content", answer=raw_text.strip())]

    faqs = []
    for question, answer in matches:
        faqs.append(FAQItem(question=question.strip(), answer=answer.strip()))

    return faqs