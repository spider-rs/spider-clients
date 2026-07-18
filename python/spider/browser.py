"""
Browser automation integration for the Spider Cloud client.

Re-exports the public API of the standalone `spider-browser` package
(https://pypi.org/project/spider-browser/) so browser automation is
available directly from the `spider` package, mirroring the JS and Go
clients:

    from spider import Spider, SpiderBrowserOptions, LLMConfig

    app = Spider(api_key="sk-xxx")
    async with app.browser() as browser:
        await browser.page.goto("https://example.com")
        html = await browser.page.content()
"""

# Browser automation
from spider_browser import (
    SpiderBrowser,
    SpiderBrowserOptions,
    SpiderPage,
    BrowserType,
    SpiderEventEmitter,
)

# Browser AI
from spider_browser import (
    Agent,
    AgentOptions,
    AgentResult,
    LLMConfig,
    create_provider,
)
from spider_browser.ai.act import act
from spider_browser.ai.observe import observe, ObserveResult
from spider_browser.ai.extract import extract

# Smart retry
from spider_browser.retry.retry_engine import RetryEngine, RetryContext

__all__ = [
    # Browser automation
    "SpiderBrowser",
    "SpiderBrowserOptions",
    "SpiderPage",
    "BrowserType",
    "SpiderEventEmitter",
    # Browser AI
    "Agent",
    "AgentOptions",
    "AgentResult",
    "LLMConfig",
    "create_provider",
    "act",
    "observe",
    "extract",
    "ObserveResult",
    # Smart retry
    "RetryEngine",
    "RetryContext",
]
