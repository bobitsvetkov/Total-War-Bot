import pytest


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("75%", 75.0),
        ("0%", 0.0),
        ("100%", 100.0),
        (None, 0.0),
        ("", 0.0),
        ("invalid", 0.0),
        ("50.5%", 50.5),
    ],
)
def test_parse_percentage(historical_results, input_str, expected):
    """Test parsing percentage strings."""
    result = historical_results._parse_percentage(input_str)
    assert result == expected
