"""Numeric JSON fields in Gateway requests must not accept booleans as numbers."""

import pytest
from pydantic import ValidationError

from app.gateway.routers.assistants_compat import AssistantSearchRequest
from app.gateway.routers.auth import PATCreateRequest
from app.gateway.routers.feedback import FeedbackCreateRequest, FeedbackUpsertRequest
from app.gateway.routers.integrations import LarkConfigCompleteRequest
from app.gateway.routers.memory import FactCreateRequest, FactPatchRequest
from app.gateway.routers.subagents import ManagedSubagentCreateRequest, ManagedSubagentUpdateRequest
from app.gateway.routers.suggestions import SuggestionsRequest
from app.gateway.routers.threads import ThreadGoalRequest, ThreadHistoryRequest, ThreadSearchRequest


@pytest.mark.parametrize(
    ("request_model", "payload", "field"),
    [
        (AssistantSearchRequest, {}, "limit"),
        (AssistantSearchRequest, {}, "offset"),
        (PATCreateRequest, {"name": "automation", "scopes": ["threads:read"]}, "expires_in_days"),
        (FeedbackCreateRequest, {}, "rating"),
        (FeedbackUpsertRequest, {}, "rating"),
        (LarkConfigCompleteRequest, {"device_code": "device", "generation": "generation"}, "interval"),
        (LarkConfigCompleteRequest, {"device_code": "device", "generation": "generation"}, "expires_in"),
        (FactCreateRequest, {"content": "fact"}, "confidence"),
        (FactPatchRequest, {}, "confidence"),
        (ManagedSubagentCreateRequest, {"name": "planner", "description": "Plans", "system_prompt": "Plan."}, "max_turns"),
        (ManagedSubagentCreateRequest, {"name": "planner", "description": "Plans", "system_prompt": "Plan."}, "timeout_seconds"),
        (ManagedSubagentUpdateRequest, {}, "max_turns"),
        (ManagedSubagentUpdateRequest, {}, "timeout_seconds"),
        (SuggestionsRequest, {"messages": []}, "n"),
        (ThreadGoalRequest, {"objective": "Finish the task"}, "max_continuations"),
        (ThreadHistoryRequest, {}, "limit"),
        (ThreadSearchRequest, {}, "limit"),
        (ThreadSearchRequest, {}, "offset"),
    ],
)
def test_gateway_numeric_request_fields_reject_true(request_model, payload, field):
    with pytest.raises(ValidationError, match="not a boolean"):
        request_model.model_validate({**payload, field: True})


@pytest.mark.parametrize(
    ("request_model", "payload", "field"),
    [
        (FeedbackCreateRequest, {}, "rating"),
        (FeedbackUpsertRequest, {}, "rating"),
        (LarkConfigCompleteRequest, {"device_code": "device", "generation": "generation"}, "interval"),
        (LarkConfigCompleteRequest, {"device_code": "device", "generation": "generation"}, "expires_in"),
        (FactCreateRequest, {"content": "fact"}, "confidence"),
        (FactPatchRequest, {}, "confidence"),
        (ThreadGoalRequest, {"objective": "Finish the task"}, "max_continuations"),
        (ThreadSearchRequest, {}, "offset"),
    ],
)
def test_gateway_numeric_request_fields_reject_false_when_in_range(request_model, payload, field):
    with pytest.raises(ValidationError, match="not a boolean"):
        request_model.model_validate({**payload, field: False})


@pytest.mark.parametrize(
    ("request_model", "payload", "field", "value"),
    [
        (AssistantSearchRequest, {}, "limit", 12),
        (AssistantSearchRequest, {}, "offset", 3),
        (PATCreateRequest, {"name": "automation", "scopes": ["threads:read"]}, "expires_in_days", 30),
        (FeedbackCreateRequest, {}, "rating", 1),
        (FeedbackUpsertRequest, {}, "rating", -1),
        (LarkConfigCompleteRequest, {"device_code": "device", "generation": "generation"}, "interval", 4),
        (LarkConfigCompleteRequest, {"device_code": "device", "generation": "generation"}, "expires_in", 600),
        (FactCreateRequest, {"content": "fact"}, "confidence", 0.75),
        (FactPatchRequest, {}, "confidence", 0.25),
        (ManagedSubagentCreateRequest, {"name": "planner", "description": "Plans", "system_prompt": "Plan."}, "max_turns", 7),
        (ManagedSubagentCreateRequest, {"name": "planner", "description": "Plans", "system_prompt": "Plan."}, "timeout_seconds", 120),
        (ManagedSubagentUpdateRequest, {}, "max_turns", 7),
        (ManagedSubagentUpdateRequest, {}, "timeout_seconds", 120),
        (SuggestionsRequest, {"messages": []}, "n", 2),
        (ThreadGoalRequest, {"objective": "Finish the task"}, "max_continuations", 2),
        (ThreadHistoryRequest, {}, "limit", 5),
        (ThreadSearchRequest, {}, "limit", 20),
        (ThreadSearchRequest, {}, "offset", 3),
    ],
)
def test_gateway_numeric_request_fields_preserve_numbers(request_model, payload, field, value):
    request = request_model.model_validate({**payload, field: value})
    assert getattr(request, field) == value
