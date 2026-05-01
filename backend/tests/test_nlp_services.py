import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.huggingface_nlp_service import HuggingFaceNLPService
from app.services.nlp_service import BertTriageModel

def test_huggingface_nlp_fallback_logic():
    # Test with no token to force fallback
    service = HuggingFaceNLPService(api_token=None)
    
    # Test Sentiment Fallback
    res_sent = service._fallback_sentiment("SOS! Help me, fire everywhere!")
    assert res_sent["sentiment"] == "negative"
    assert res_sent["score"] < 0
    
    res_safe = service._fallback_sentiment("Everything is safe and okay now.")
    assert res_safe["sentiment"] == "positive"
    
    # Test Classification Fallback
    res_class = service._fallback_classification("People are trapped in the building")
    assert res_class["classification"] == "request"
    
    res_report = service._fallback_classification("Huge flood in the river district")
    assert res_report["classification"] == "report"

@pytest.mark.asyncio
async def test_huggingface_nlp_analyze_mocked():
    service = HuggingFaceNLPService(api_token="fake_token")
    
    # Mock httpx responses for sentiment and classification
    with patch("httpx.AsyncClient.post") as mock_post:
        # 1. Mock Sentiment Response
        mock_resp_sent = MagicMock()
        mock_resp_sent.status_code = 200
        mock_resp_sent.json.return_value = [[{"label": "NEGATIVE", "score": 0.9}]]
        
        # 2. Mock Classification Response
        mock_resp_class = MagicMock()
        mock_resp_class.status_code = 200
        mock_resp_class.json.return_value = {
            "labels": ["request", "chatter"],
            "scores": [0.85, 0.1]
        }
        
        mock_post.side_effect = [mock_resp_sent, mock_resp_class]
        
        result = await service.analyze_text("Help me!")
        
        assert result["classification"] == "request"
        assert result["sentiment"] == "negative"
        assert result["source"] == "huggingface"
        assert result["signal_strength"] == 1.0

def test_bert_triage_model_fallback():
    # Force error in BertTriageModel to trigger its own fallback
    model = BertTriageModel()
    
    with patch.object(model.hf_service, "analyze_text", side_effect=Exception("API Down")):
        result = model.analyze_text("URGENT FIRE SOS")
        assert result["classification"] in ["request", "report", "alert"]
        assert result["source"] == "fallback"

def test_huggingface_cache_logic():
    service = HuggingFaceNLPService(api_token="fake")
    service._cache["sentiment_" + str(hash("test"))] = {"sentiment": "neutral", "score": 0.0}
    
    # This should return from cache even if httpx is not mocked (it shouldn't be called)
    import asyncio
    res = asyncio.run(service.analyze_sentiment("test"))
    assert res["sentiment"] == "neutral"
    
    service.clear_cache()
    assert len(service._cache) == 0
