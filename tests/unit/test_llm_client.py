import json

import llm_client


def test_generate_content_returns_none_when_no_providers_configured():
    result = llm_client.generate_content(
        config={},
        date_str="2026-05-10",
        papers_context="papers",
        news_context="news",
        language="zh",
    )
    assert result is None


def test_generate_content_returns_none_when_all_providers_fail(monkeypatch):
    def fake_robust_post(url, **kwargs):
        class FakeResp:
            status_code = 500
            text = "server error"

            def raise_for_status(self):
                raise Exception("API error")
        return FakeResp()

    import robust_fetch
    monkeypatch.setattr(robust_fetch, "robust_post", fake_robust_post)

    config = {
        "api_providers": [
            {
                "name": "fake-provider",
                "api_base_url": "https://fake.example.com/v1",
                "api_key": "sk-test",
                "model": "test-model",
            }
        ]
    }

    result = llm_client.generate_content(
        config=config,
        date_str="2026-05-10",
        papers_context="papers",
        news_context="news",
        language="zh",
    )
    assert result is None


def test_generate_content_returns_content_on_success(monkeypatch):
    call_log = []

    def fake_robust_post(url, **kwargs):
        class FakeResp:
            status_code = 200
            text = json.dumps({
                "choices": [{"message": {"content": "Generated report content"}}]
            })

            def raise_for_status(self):
                pass

            def json(self):
                return json.loads(self.text)
        call_log.append(url)
        return FakeResp()

    import robust_fetch
    monkeypatch.setattr(robust_fetch, "robust_post", fake_robust_post)

    # Stub history_db so we don't need a real database
    import history_db
    monkeypatch.setattr(history_db, "get_recent_projects", lambda limit=20: [])
    monkeypatch.setattr(history_db, "get_recent_papers_titles", lambda limit=10: [])
    monkeypatch.setattr(history_db, "update_history_from_content", lambda content: [])

    config = {
        "api_providers": [
            {
                "name": "test-provider",
                "api_base_url": "https://test.example.com/v1",
                "api_key": "sk-test",
                "model": "test-model",
            }
        ]
    }

    result = llm_client.generate_content(
        config=config,
        date_str="2026-05-10",
        papers_context="some papers",
        news_context="some news",
        language="en",
    )

    assert result == "Generated report content"
    assert len(call_log) == 1
    assert "test.example.com" in call_log[0]
