from __future__ import annotations

import pytest
from pydantic import ValidationError

from deerflow.config.app_config import AppConfig
from deerflow.config.read_before_write_config import ReadBeforeWriteConfig


@pytest.mark.parametrize("value", [True, False])
def test_app_config_rejects_boolean_read_before_write_min_chars(value: bool) -> None:
    with pytest.raises(ValidationError, match="elide_min_chars must be an integer, not a boolean"):
        AppConfig.model_validate(
            {
                "sandbox": {"use": "deerflow.sandbox.local:LocalSandboxProvider"},
                "read_before_write": {"elide_min_chars": value},
            }
        )


def test_read_before_write_min_chars_preserves_integer_and_numeric_string_values() -> None:
    assert ReadBeforeWriteConfig(elide_min_chars=0).elide_min_chars == 0
    assert ReadBeforeWriteConfig(elide_min_chars=2000).elide_min_chars == 2000
    assert ReadBeforeWriteConfig(elide_min_chars="17").elide_min_chars == 17
