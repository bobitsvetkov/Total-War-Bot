import pytest
from unittest.mock import patch, MagicMock
from utils.gemini_prompt import generate_analysis

all_factions_stats = {
    "Rome": {
        "survivability": 75,
        "melee_strength": 88.08,
        "ranged_strength": 45,
        "cavalry_prowess": 60,
        "pilla_prowess": 50,
    },
    "Boii": {
        "survivability": 70,
        "melee_strength": 80.08,
        "ranged_strength": 40,
        "cavalry_prowess": 55,
        "pilla_prowess": 45,
    },
}


@pytest.fixture
def mock_genai_response():
    """Fixture to mock the response from the generative AI."""

    def _mock_response(
        text="Boii is a balanced faction with strengths in melee combat but weaknesses in ranged attacks.",
    ):
        mock_response = MagicMock()
        mock_response.text = text
        return mock_response

    return _mock_response


@patch("google.generativeai.GenerativeModel")
def test_generate_analysis(mock_genai_model, mock_genai_response):
    """Test the generate_analysis function with mocked generative AI."""
    mock_genai_model.return_value.generate_content.return_value = mock_genai_response()
    result = generate_analysis("Boii", all_factions_stats["Boii"], all_factions_stats)
    assert result == mock_genai_model.return_value.generate_content.return_value.text
