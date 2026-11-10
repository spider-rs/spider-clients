"""LangChain standard unit tests for the Spider tools."""

from __future__ import annotations

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_spider import SpiderScrapeTool, SpiderSearchTool


class TestSpiderScrapeToolStandard(ToolsUnitTests):
    @property
    def tool_constructor(self) -> type[SpiderScrapeTool]:
        return SpiderScrapeTool

    @property
    def tool_constructor_params(self) -> dict:
        return {"api_key": "test-key"}

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"url": "https://example.com"}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        return {"SPIDER_API_KEY": "env-key"}, {}, {"api_key": "env-key"}


class TestSpiderSearchToolStandard(ToolsUnitTests):
    @property
    def tool_constructor(self) -> type[SpiderSearchTool]:
        return SpiderSearchTool

    @property
    def tool_constructor_params(self) -> dict:
        return {"api_key": "test-key"}

    @property
    def tool_invoke_params_example(self) -> dict:
        return {"query": "rust web crawler", "search_limit": 3}

    @property
    def init_from_env_params(self) -> tuple[dict, dict, dict]:
        return {"SPIDER_API_KEY": "env-key"}, {}, {"api_key": "env-key"}
