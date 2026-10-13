import asyncio
import json

from backend.app.api.nlp import TextRequest, extract_entities


def test_extract_entities_returns_json_safe_extractor_entities():
    result = asyncio.run(extract_entities(TextRequest(text="Virat Kohli hit a four for India")))

    assert result["player_mentions"]
    assert result["team_mentions"]
    assert all("entity_type" in entity and "original" in entity for entity in result["entities"])
    json.dumps(result)
