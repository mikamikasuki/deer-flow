"""Regression tests for Claude manual extended-thinking token budgets."""

from unittest import mock

import pytest

from deerflow.models.claude_provider import ClaudeChatModel


def _make_model(*, oauth: bool = False) -> ClaudeChatModel:
    """Return a Claude provider without credential loading or network access."""
    with mock.patch.object(ClaudeChatModel, "model_post_init"):
        model = ClaudeChatModel(
            model="claude-sonnet-4-5",
            anthropic_api_key="sk-ant-fake",  # type: ignore[call-arg]
        )
    model._is_oauth = oauth
    return model


def test_automatic_budget_respects_minimum_when_max_tokens_has_room() -> None:
    model = _make_model()
    payload = {"max_tokens": 1025, "thinking": {"type": "enabled"}}

    model._apply_thinking_budget(payload)

    assert payload["thinking"]["budget_tokens"] == 1024


def test_automatic_budget_rejects_too_small_max_tokens_without_interleaving() -> None:
    model = _make_model()
    payload = {"max_tokens": 512, "thinking": {"type": "enabled"}}

    with pytest.raises(ValueError, match="max_tokens must exceed the 1024-token"):
        model._apply_thinking_budget(payload)


def test_explicit_budget_below_provider_minimum_is_rejected() -> None:
    model = _make_model()
    payload = {
        "max_tokens": 4096,
        "thinking": {"type": "enabled", "budget_tokens": 512},
    }

    with pytest.raises(ValueError, match="budget_tokens must be at least 1024"):
        model._apply_thinking_budget(payload)


def test_explicit_budget_must_leave_room_for_final_answer_without_interleaving() -> None:
    model = _make_model()
    payload = {
        "max_tokens": 1024,
        "thinking": {"type": "enabled", "budget_tokens": 1024},
    }

    with pytest.raises(ValueError, match="budget_tokens must be less than max_tokens"):
        model._apply_thinking_budget(payload)


def test_interleaved_oauth_allows_budget_to_exceed_max_tokens() -> None:
    model = _make_model(oauth=True)
    payload = {
        "max_tokens": 512,
        "thinking": {"type": "enabled", "budget_tokens": 1024},
    }

    model._apply_thinking_budget(payload)

    assert payload["thinking"]["budget_tokens"] == 1024


def test_automatic_interleaved_oauth_budget_is_clamped_to_provider_minimum() -> None:
    model = _make_model(oauth=True)
    payload = {"max_tokens": 512, "thinking": {"type": "enabled"}}

    model._apply_thinking_budget(payload)

    assert payload["thinking"]["budget_tokens"] == 1024


def test_explicit_budget_uses_interleaved_beta_from_default_headers() -> None:
    model = _make_model()
    model.default_headers = {"anthropic-beta": "other-beta, interleaved-thinking-2025-05-14"}
    payload = {
        "max_tokens": 1024,
        "thinking": {"type": "enabled", "budget_tokens": 1024},
    }

    model._apply_thinking_budget(payload)

    assert payload["thinking"]["budget_tokens"] == 1024
