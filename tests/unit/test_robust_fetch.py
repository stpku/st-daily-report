import importlib
from unittest.mock import patch, MagicMock

import robust_fetch


def test_robust_get_uses_session_with_retry():
    """robust_get should build a session with retry adapter."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_session.get.return_value = mock_response

    with patch("robust_fetch._build_session", return_value=mock_session):
        resp = robust_fetch.robust_get("https://example.com")

    assert resp.status_code == 200
    mock_session.get.assert_called_once()


def test_robust_get_applies_default_timeout():
    """When no timeout is given, the session default should be used."""
    mock_session = MagicMock()
    mock_session.request_timeout = 42
    mock_session.get.return_value = MagicMock()

    with patch("robust_fetch._build_session", return_value=mock_session):
        robust_fetch.robust_get("https://example.com")

    call_kwargs = mock_session.get.call_args
    assert call_kwargs[1].get("timeout") == 42


def test_robust_get_allows_caller_timeout_override():
    """Caller-provided timeout should take precedence."""
    mock_session = MagicMock()
    mock_session.request_timeout = 42
    mock_session.get.return_value = MagicMock()

    with patch("robust_fetch._build_session", return_value=mock_session):
        robust_fetch.robust_get("https://example.com", timeout=10)

    call_kwargs = mock_session.get.call_args
    assert call_kwargs[1].get("timeout") == 10


def test_robust_post_passes_json_and_headers():
    """robust_post should forward json payload and headers."""
    mock_session = MagicMock()
    mock_session.post.return_value = MagicMock()

    with patch("robust_fetch._build_session", return_value=mock_session):
        robust_fetch.robust_post(
            "https://example.com/api",
            json={"key": "value"},
            headers={"Authorization": "Bearer token"},
        )

    call_kwargs = mock_session.post.call_args
    assert call_kwargs[1].get("json") == {"key": "value"}
    assert call_kwargs[1].get("headers") == {"Authorization": "Bearer token"}


def test_build_session_mounts_retry_adapter():
    """_build_session should mount retry adapters on both schemes."""
    session = robust_fetch._build_session(total_retries=2)
    # HTTPAdapter has a max_retries attribute
    adapter = session.get_adapter("https://example.com")
    assert adapter.max_retries.total == 2
