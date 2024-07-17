import pytest
import os
from unittest.mock import patch, MagicMock
from spider.async_spider import AsyncSpider
from spider.spider_types import RequestParamsDict
import aiohttp
from aiohttp import ClientResponse
from typing import AsyncIterator

@pytest.fixture
def async_spider():
    return AsyncSpider(api_key="test_api_key")

@pytest.fixture
def url():
    return "http://example.com"

@pytest.fixture
def params():
    return {
        "limit": 1,
        "return_format": "markdown",
        "depth": 2,
        "cache": True,
        "domain": "example.com",
    }

@pytest.mark.asyncio
async def test_init_with_env_variable():
    os.environ["SPIDER_API_KEY"] = "env_api_key"
    spider = AsyncSpider()
    assert spider.api_key == "env_api_key"
    del os.environ["SPIDER_API_KEY"]

def test_init_without_api_key():
    with pytest.raises(ValueError):
        AsyncSpider(api_key=None)

@pytest.mark.asyncio
async def test_scrape_url(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"content": "data", "error": None, "status": 200, "url": url}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.scrape_url(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_crawl_url(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"content": "data", "error": None, "status": 200, "url": url}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.crawl_url(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_links(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"error": None, "status": 200, "url": url}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.links(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_screenshot(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"content": "base64_encoded_image", "error": None, "status": 200, "url": url}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.screenshot(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_search(async_spider, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"content": "result", "error": None, "status": 200, "url": "http://example.com"}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.search("example search query", params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_transform(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = {"content": "transformed", "error": None, "status": 200}

    transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.transform(transform_data, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]

@pytest.mark.asyncio
async def test_extract_contacts(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"content": "contacts", "error": None, "status": 200, "url": url}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.extract_contacts(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_label(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = [{"content": "labels", "error": None, "status": 200, "url": url}]

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.label(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.asyncio
async def test_get_crawl_state(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = {"data": [{"state": "completed", "credits_used": 10}]}

    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.get_crawl_state(url, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'data' in response[0]
        assert isinstance(response[0]['data'], list)

@pytest.mark.asyncio
async def test_get_credits(async_spider):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = {"data": [{"credits": 1000}]}

    with patch.object(AsyncSpider, 'api_get', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.get_credits()]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'data' in response[0]
        assert isinstance(response[0]['data'], list)

@pytest.mark.asyncio
async def test_data_post(async_spider, url):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 204

    table = "websites"
    post_data: RequestParamsDict = {"url": url}
    with patch.object(AsyncSpider, 'api_post', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.data_post(table, post_data)]
        assert len(response) > 0
        assert response[0] is not None

@pytest.mark.asyncio
async def test_data_get(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json.return_value = {"data": [{"url": url}]}

    table = "websites"
    with patch.object(AsyncSpider, 'api_get', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.data_get(table, params=params)]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'data' in response[0]
        assert isinstance(response[0]['data'], list)

@pytest.mark.asyncio
async def test_data_delete(async_spider, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 204

    table = "websites"
    with patch.object(AsyncSpider, 'api_delete', return_value=AsyncIterator([mock_response])):
        response = [r async for r in async_spider.data_delete(table, params=params)]
        assert len(response) > 0
        assert response[0] is not None

@pytest.mark.asyncio
async def test_stream_reader(async_spider):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.content.iter_any.return_value = [
        b'{"key": "value"}\n',
        b'{"key2": "value2"}\n'
    ]
    
    callback_data = []
    def callback(json_obj):
        callback_data.append(json_obj)
    
    async for _ in async_spider.stream_reader(mock_response, callback):
        pass
    
    assert len(callback_data) == 2
    assert callback_data[0] == {"key": "value"}
    assert callback_data[1] == {"key2": "value2"}

@pytest.mark.asyncio
async def test_handle_error(async_spider):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 402
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.json.return_value = {"error": "Payment Required"}
    
    with pytest.raises(Exception, match="Failed to test action. Status code: 402. Error: Payment Required"):
        await async_spider._handle_error(mock_response, "test action")