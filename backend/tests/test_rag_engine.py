import os
import unittest
from unittest.mock import patch

from backend.app.rag.engine import BALLRIQRAGEngine


class _Hybrid:
    def __init__(self, documents):
        self.documents = documents

    def search(self, *args, **kwargs):
        return self.documents


class RAGEngineTests(unittest.TestCase):
    def setUp(self):
        self.documents = [{
            "document_id": "M1_1", "match_id": "M1", "over": 10, "ball": 2,
            "event_type": "FOUR", "language": "en", "score": 0.9,
            "content": "Kohli drove through cover for four.",
        }]
        self.components = ([], None, None, _Hybrid(self.documents))

    @patch("backend.app.rag.engine.get_ir_components")
    def test_uses_labelled_quote_only_fallback_with_sources(self, get_components):
        get_components.return_value = self.components
        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENAI_MODEL": ""}, clear=False):
            result = BALLRIQRAGEngine().answer_question("What happened?", language="en")

        self.assertEqual(result["generation"], "deterministic_evidence_fallback")
        self.assertIn(self.documents[0]["content"], result["answer"])
        self.assertIn("[1]", result["answer"])
        self.assertEqual(result["citations"], result["sources"])
        self.assertEqual(result["citations"][0]["document_id"], "M1_1")

    @patch("backend.app.rag.engine.get_ir_components")
    def test_insufficient_evidence_still_returns_empty_source_fields(self, get_components):
        get_components.return_value = ([], None, None, _Hybrid([]))
        result = BALLRIQRAGEngine().answer_question("What happened?", language="en")

        self.assertFalse(result["is_grounded"])
        self.assertEqual(result["citations"], [])
        self.assertEqual(result["sources"], [])

    @patch("backend.app.rag.engine.get_ir_components")
    def test_custom_generator_is_explicit_and_keeps_external_citations(self, get_components):
        get_components.return_value = self.components
        result = BALLRIQRAGEngine(lambda *_: "Supported answer [1]").answer_question(
            "What happened?", language="en"
        )

        self.assertEqual(result["generation"], "custom_generator")
        self.assertEqual(result["answer"], "Supported answer [1]")
        self.assertEqual(len(result["sources"]), 1)


if __name__ == "__main__":
    unittest.main()
