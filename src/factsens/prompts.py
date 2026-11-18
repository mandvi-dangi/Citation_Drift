"""Fixed prompt template. Abstention wording is part of the frozen protocol."""
from .data import LETTERS
import hashlib

TEMPLATE = (
    "Answer the multiple-choice question below. If you are not sure, you may abstain.\n"
    "Reply in exactly this format:\n"
    "ANSWER: <letter, or NS if you are not sure>\n"
    "CONFIDENCE: <integer 0-100, your probability that your answer is correct; 0 if NS>\n\n"
    "Question: {question}\n{options}\n"
)

def build_prompt(item):
    opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(item["options"]))
    return TEMPLATE.format(question=item["question"], options=opts)

def prompt_hash(prompt):
    return hashlib.sha256(prompt.encode()).hexdigest()[:12]
