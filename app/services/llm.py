from typing import Any

from google import genai
from google.genai import types

SYSTEM_INSTRUCTION_TEMPLATE = """You are a question-answering assistant grounded in the provided CONTEXT.

Rules:
- Answer ONLY using information present in the CONTEXT below.
- Do NOT use prior knowledge or external facts.
- If the CONTEXT does not contain enough information to answer the question, reply EXACTLY with:
  {refusal}
- When you state a fact, cite its origin inline as [source, page N].
- Be concise and direct."""


class LLMClient:
    def __init__(self, api_key: str, model: str, refusal: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.refusal = refusal
        self.system_instruction = SYSTEM_INSTRUCTION_TEMPLATE.format(refusal=refusal)

    def answer(self, question: str, context_chunks: list[dict[str, Any]]) -> str:
        if not context_chunks:
            return self.refusal

        context_block = "\n\n".join(
            f"[{c['metadata']['source']}, page {c['metadata']['page']}]\n{c['text']}"
            for c in context_chunks
        )
        prompt = f"CONTEXT:\n{context_block}\n\nQUESTION: {question}"

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.0,
            ),
        )
        return (response.text or self.refusal).strip()
