import pytest
import requests
from conftest import MockResponse

from api import collect_nass


@pytest.fixture
def mock_response(monkeypatch):
    """Mock of requests.get()"""
    response = MockResponse()

    def mock_get(*args, **kwargs):
        # record each call into MockResponse
        response.calls.append((args, kwargs))
        return response

    # monkeypatch swap requests.get for mock_get
    monkeypatch.setattr(requests, "get", mock_get)
    return response


def test_get_NASS_data_rejects_50001_rows(mock_response):
    with pytest.raises(ValueError, match="Request too large"):
        collect_nass.get_NASS_data("url", 50001, {})

    assert mock_response.calls == []


def test_get_NASS_data_allows_row_count_at_limit(mock_response):
    mock_response.json_data = {"data": [{"Value": "1"}]}

    df = collect_nass.get_NASS_data("url", 50000, {})

    assert len(df) == 1
