"""The LangGraph graph factory must load config outside its event loop."""

from __future__ import annotations

import asyncio
import importlib
import inspect
import json
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_configured_langgraph_factory_offloads_config_loading(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "config.yaml"
    await asyncio.to_thread(
        config_path.write_text,
        "config_version: 53\nsandbox:\n  use: deerflow.sandbox.local:LocalSandboxProvider\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DEER_FLOW_CONFIG_PATH", str(config_path))

    importlib.import_module("deerflow.agents")
    lead_agent = await asyncio.to_thread(importlib.import_module, "deerflow.agents.lead_agent")
    config_module = await asyncio.to_thread(importlib.import_module, "deerflow.config.app_config")
    AppConfig = config_module.AppConfig
    get_app_config = config_module.get_app_config
    reset_app_config = config_module.reset_app_config

    reset_app_config()
    monkeypatch.setattr(lead_agent, "make_lead_agent", lambda config: get_app_config())
    langgraph_config = json.loads(await asyncio.to_thread((BACKEND_DIR / "langgraph.json").read_text, encoding="utf-8"))
    module_name, factory_name = langgraph_config["graphs"]["lead_agent"].split(":", 1)
    module = importlib.import_module(module_name)
    factory = module.__dict__[factory_name]

    try:
        if inspect.iscoroutinefunction(factory):
            loaded = await factory({"configurable": {}})
        else:
            loaded = factory({"configurable": {}})
        assert isinstance(loaded, AppConfig)
        assert loaded.sandbox.use == "deerflow.sandbox.local:LocalSandboxProvider"
    finally:
        reset_app_config()
