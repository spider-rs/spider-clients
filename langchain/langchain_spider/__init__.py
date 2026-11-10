"""Spider integration for LangChain: a document loader and web tools."""

from langchain_spider._client import SpiderAPIError, __version__
from langchain_spider.document_loaders import SpiderLoader
from langchain_spider.tools import SpiderScrapeTool, SpiderSearchTool, SpiderToolkit

__all__ = [
    "SpiderAPIError",
    "SpiderLoader",
    "SpiderScrapeTool",
    "SpiderSearchTool",
    "SpiderToolkit",
    "__version__",
]
