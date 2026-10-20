"""Grounded multilingual RAG answers with optional OpenAI-compatible generation."""
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx

from backend.app.api.ir import get_ir_components
from backend.app.nlp.preprocessing.language_processing import identify_language


AnswerGenerator = Callable[[str, str, List[Dict[str, Any]]], str]


class BALLRIQRAGEngine:
    """Retrieve evidence first, then answer only from the returned evidence."""

    def __init__(self, answer_generator: Optional[AnswerGenerator] = None):
        # A callable is useful for a locally hosted provider or controlled tests.
        self.answer_generator = answer_generator

    def answer_question(self, question: str, match_id: Optional[str] = None,
                        language: str = "auto") -> Dict[str, Any]:
        lang = self._language(question, language)
        _, _, _, hybrid = get_ir_components()
        search_k = 100 if match_id else 6
        retrieved_docs = hybrid.search(question, top_k=search_k, alpha=0.5)
        if match_id:
            match_docs = [doc for doc in retrieved_docs if doc.get("match_id") == match_id]
            retrieved_docs = match_docs if match_docs else retrieved_docs[:6]

        citations = self._citations(retrieved_docs[:4])
        if not retrieved_docs or retrieved_docs[0].get("score", 0) < 0.05:
            return self._no_evidence(question, lang)

        try:
            answer, generator = self._generate(question, lang, citations)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            answer, generator = self._deterministic_answer(lang, citations), "deterministic_evidence_fallback"

        return {
            "question": question,
            "language": lang,
            "answer": answer,
            "confidence": round(min(0.95, retrieved_docs[0].get("score", 0.8) + 0.15), 2),
            "is_grounded": True,
            "generation": generator,
            "citations": citations,
            "sources": citations,
            "retrieved_context_count": len(retrieved_docs),
        }

    @staticmethod
    def _language(question: str, language: str) -> str:
        if language != "auto":
            return language if language in {"hi", "mr", "en"} else "en"
        detected = identify_language(question).language
        return detected if detected in {"hi", "mr", "en"} else "en"

    @staticmethod
    def _citations(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{
            "citation_id": index,
            "document_id": doc.get("document_id"),
            "match_id": doc.get("match_id"),
            "over": doc.get("over"),
            "ball": doc.get("ball"),
            "event_type": doc.get("event_type"),
            "language": doc.get("language"),
            "score": round(doc.get("score", 0), 4),
            "snippet": doc.get("content", ""),
        } for index, doc in enumerate(documents, 1)]

    def _generate(self, question: str, language: str,
                  citations: List[Dict[str, Any]]) -> Tuple[str, str]:
        if self.answer_generator:
            return self.answer_generator(question, language, citations).strip(), "custom_generator"
        if self._provider_configured():
            return self._openai_answer(question, language, citations), "openai_compatible"
        return self._deterministic_answer(language, citations), "deterministic_evidence_fallback"

    @staticmethod
    def _provider_configured() -> bool:
        return bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_MODEL"))

    @staticmethod
    def _openai_answer(question: str, language: str,
                       citations: List[Dict[str, Any]]) -> str:
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        evidence = "\n".join(
            f"[{item['citation_id']}] match={item['match_id']}, over={item['over']}.{item['ball']}: {item['snippet']}"
            for item in citations
        )
        payload = {
            "model": os.environ["OPENAI_MODEL"], "temperature": 0,
            "messages": [
                {"role": "system", "content": (
                    "Answer only from the supplied cricket evidence. Do not infer, calculate, "
                    "or add facts. If it does not answer the question, say that evidence is insufficient. "
                    "Use only citations in the form [n] that appear in the evidence."
                )},
                {"role": "user", "content": f"Answer in {language}.\nQuestion: {question}\nEvidence:\n{evidence}"},
            ],
        }
        response = httpx.post(
            f"{base_url}/chat/completions", json=payload,
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}, timeout=20,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"].strip()
        if not answer:
            raise ValueError("Empty provider answer")
        return answer

    @staticmethod
    def _deterministic_answer(language: str, citations: List[Dict[str, Any]]) -> str:
        top = citations[0]
        if language == "hi":
            return f"निर्धारित साक्ष्य-संश्लेषण: उपलब्ध टिप्पणी में लिखा है: “{top['snippet']}” [{top['citation_id']}]"
        if language == "mr":
            return f"निर्धारित पुरावा-संश्लेषण: उपलब्ध समालोचनामध्ये असे नमूद आहे: “{top['snippet']}” [{top['citation_id']}]"
        return f"Deterministic evidence synthesis: the retrieved commentary states: “{top['snippet']}” [{top['citation_id']}]"

    @staticmethod
    def _no_evidence(question: str, language: str) -> Dict[str, Any]:
        messages = {
            "hi": "उपलब्ध मैच डेटा में इस प्रश्न के लिए पर्याप्त साक्ष्य नहीं मिले।",
            "mr": "उपलब्ध मॅच डेटामध्ये या प्रश्नासाठी पुरेसा पुरावा सापडला नाही.",
            "en": "I could not find sufficient evidence in the available match data.",
        }
        return {
            "question": question, "language": language, "answer": messages[language],
            "confidence": 0.2, "is_grounded": False,
            "generation": "insufficient_evidence", "citations": [], "sources": [],
            "retrieved_context_count": 0,
        }
