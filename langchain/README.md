# langchain-spider

LangChain integration for [Spider](https://spider.cloud/?utm_source=langchain&utm_medium=directory&utm_campaign=langchain-listing). It has four classes:

| Class | Kind | Spider route | Returns |
|---|---|---|---|
| `SpiderScrapeTool` | Tool | `POST /scrape` | One page as markdown, text or raw HTML |
| `SpiderSearchTool` | Tool | `POST /search` | Ranked results with title, description and URL, or each result's page content |
| `SpiderToolkit` | Toolkit | both of the above | `[SpiderSearchTool, SpiderScrapeTool]` with shared settings |
| `SpiderLoader` | Document loader | `POST /scrape` or `POST /crawl` | One `Document` per page |

It depends on `langchain-core` and `httpx` and nothing else.

## Install

```bash
pip install -U langchain-spider
```

## API key

Create a key at [spider.cloud/api-keys](https://spider.cloud/api-keys?utm_source=langchain&utm_medium=directory&utm_campaign=langchain-listing) and set it in the environment:

```bash
export SPIDER_API_KEY=your-key
```

Every class also takes `api_key=`. `SpiderScrapeTool` and `SpiderLoader` in scrape mode work without a key, on a rate limited keyless tier. Search and crawl need a key.

## Tools

```python
from langchain_spider import SpiderScrapeTool, SpiderSearchTool

search = SpiderSearchTool()
search.invoke({"query": "rust web crawler", "search_limit": 3})
# [{"title": "...", "description": "...", "url": "https://..."}, ...]

scrape = SpiderScrapeTool(max_content_chars=20_000)
scrape.invoke({"url": "https://spider.cloud"})
# "# Spider ..." (markdown)
```

Give them to an agent. `SpiderToolkit` builds both tools with the same settings:

```python
from langchain.agents import create_agent
from langchain_spider import SpiderToolkit

agent = create_agent(
    model="openai:gpt-5-mini",
    tools=SpiderToolkit(max_content_chars=20_000).get_tools(),
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Summarize the latest Rust release notes."}]}
)
```

The model can set these arguments:

- `spider_scrape`: `url`, `return_format` (`markdown`, `text`, `raw`), `request` (`smart`, `http`, `browser`)
- `spider_search`: `query`, `search_limit`, `fetch_page_content`, `country`, `language`, `tbs` (`qdr:h`, `qdr:d`, `qdr:w`, `qdr:m`, `qdr:y`)

Options you set when you create a tool:

| Option | Default | Meaning |
|---|---|---|
| `api_key` | `SPIDER_API_KEY` env var | Spider API key, stored as a `SecretStr` |
| `params` | `{}` | Spider request fields sent on every call, such as `{"request": "browser", "readability": True}`. The model's arguments override them. |
| `max_content_chars` | `None` | Cut each page's content to this length |
| `default_search_limit` | `5` | `SpiderSearchTool` only. Result count when the model sets none |
| `base_url` | `https://api.spider.cloud` | API base URL |
| `timeout` | `120` | Request timeout in seconds |
| `client`, `async_client` | `None` | `httpx` clients to reuse |
| `handle_tool_error` | `True` | Return API errors to the model as the tool result. Set `False` to raise `ToolException`. |

## Document loader

```python
from langchain_spider import SpiderLoader

# One page
docs = SpiderLoader("https://spider.cloud").load()

# A crawl, one Document per page
loader = SpiderLoader(
    "https://spider.cloud",
    mode="crawl",
    params={"limit": 10, "return_format": "markdown", "metadata": True},
)
for doc in loader.lazy_load():
    print(doc.metadata["source"], len(doc.page_content))
```

`alazy_load()` and `aload()` work the same way with `httpx.AsyncClient`.

`params` defaults to `{"return_format": "markdown", "metadata": True}`. Pages with no content are skipped. Each Document's metadata holds the page metadata from Spider plus `source` (the page URL) and `status`.

The constructor matches the `SpiderLoader` in `langchain-community`: `url`, then `api_key`, `mode` and `params` as keyword arguments. To switch, change the import to `from langchain_spider import SpiderLoader`. This version calls the API over `httpx`, so `spider-client` is no longer needed.

The full list of request fields is in the [OpenAPI spec](https://spider.cloud/openapi.yaml?utm_source=langchain&utm_medium=directory&utm_campaign=langchain-listing).

## Errors

A non 2xx answer raises `SpiderAPIError` with `status_code`, `body` and, on 429, `retry_after` in seconds from the `Retry-After` header. The tools wrap it in `ToolException` and keep it as `__cause__`.

## Develop

```bash
pip install -e ".[test,lint]"
pytest
ruff check . && ruff format --check .
```

The unit tests use `httpx.MockTransport`, and `pytest-socket` blocks the network while they run. They include the LangChain standard `ToolsUnitTests` from `langchain-tests`.

## License

MIT
