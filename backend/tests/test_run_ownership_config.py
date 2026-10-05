from __future__ import annotations

import pytest
from pydantic import ValidationError

from deerflow.config.app_config import AppConfig
from deerflow.config.run_ownership_config import RunOwnershipConfig


@pytest.mark.parametrize("value", [True, False])
def test_app_config_rejects_boolean_run_ownership_grace(value: bool) -> None:
    with pytest.raises(ValidationError, match="grace_seconds must be an integer, not a boolean"):
        AppConfig.model_validate(
            {
                "sandbox": {"use": "deerflow.sandbox.local:LocalSandboxProvider"},
                "run_ownership": {"grace_seconds": value},
            }
        )


def test_run_ownership_grace_preserves_integer_and_numeric_string_values() -> None:
    assert RunOwnershipConfig(grace_seconds=0).grace_seconds == 0
    assert RunOwnershipConfig(grace_seconds=10).grace_seconds == 10
    assert RunOwnershipConfig(grace_seconds="7").grace_seconds == 7
