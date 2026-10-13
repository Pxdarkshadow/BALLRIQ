"""Runtime wrapper for a locally trained XLM-R event classifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.app.nlp.preprocessing.pipeline import NLPPreprocessingPipeline


class XLMREventClassifier:
    """Load and run XLM-R artifacts written by ``scripts/train_xlmr.py``."""

    REQUIRED_FILES = ("config.json", "metadata.json")

    def __init__(self, tokenizer: Any, model: Any, metadata: Dict[str, Any]):
        self.tokenizer = tokenizer
        self.model = model
        self.metadata = metadata
        self.preprocessing_pipeline = NLPPreprocessingPipeline()
        self.max_length = int(metadata.get("max_length", 128))
        self.device = next(model.parameters()).device
        self.is_fitted = True

    @classmethod
    def artifacts_available(cls, model_dir: Path) -> bool:
        model_dir = Path(model_dir)
        return model_dir.is_dir() and all((model_dir / name).is_file() for name in cls.REQUIRED_FILES)

    @classmethod
    def load(cls, model_dir: Path) -> "XLMREventClassifier":
        model_dir = Path(model_dir)
        if not cls.artifacts_available(model_dir):
            raise FileNotFoundError(f"Incomplete XLM-R artifacts in {model_dir}")
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("XLM-R artifacts exist, but torch and transformers must be installed to use them") from exc
        with (model_dir / "metadata.json").open(encoding="utf-8") as file:
            metadata = json.load(file)
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
        model.to("cuda" if torch.cuda.is_available() else "cpu")
        model.eval()
        return cls(tokenizer, model, metadata)

    def predict_single(self, text: str) -> Dict[str, Any]:
        import torch
        processed = self.preprocessing_pipeline.process(text)
        inputs = self.tokenizer(processed.final_text, truncation=True, max_length=self.max_length, return_tensors="pt")
        inputs = {name: value.to(self.device) for name, value in inputs.items()}
        with torch.no_grad():
            probabilities = torch.softmax(self.model(**inputs).logits[0], dim=-1).cpu().tolist()
        labels = {int(key): value for key, value in self.model.config.id2label.items()}
        all_probabilities = {labels[index]: float(value) for index, value in enumerate(probabilities)}
        predicted_event = max(all_probabilities, key=all_probabilities.get)
        return {"predicted_event": predicted_event, "confidence": all_probabilities[predicted_event],
                "all_probabilities": all_probabilities, "preprocessed_text": processed.final_text,
                "detected_language": processed.detected_language}
