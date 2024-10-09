import pytest
import os
from unittest.mock import patch, AsyncMock
from spider.async_spider import AsyncSpider
from spider.spider_types import RequestParamsDict
from dotenv import load_dotenv
import aiohttp
import json

load_dotenv()

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

def test_init_with_env_variable():
    os.environ["SPIDER_API_KEY"] = "env_api_key"
    spider = AsyncSpider()
    assert spider.api_key == "env_api_key"
    del os.environ["SPIDER_API_KEY"]

def test_init_without_api_key():
    with pytest.raises(ValueError):
        AsyncSpider(api_key=None)

@pytest.mark.asyncio
async def test_scrape_url(async_spider, url, params):
    mock_response = [{"content": "data", "error": None, "status": 200, "url": url}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.scrape_url(url, params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_crawl_url(async_spider, url, params):
    mock_response = [{"content": "data", "error": None, "status": 200, "url": url}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.crawl_url(url, params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_crawl_url_streaming(async_spider, url, params):
    mock_response = b'{"url": "http://example.com"}'
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        def handle_json(json_obj):
            json_obj = json.loads(json_obj.decode('utf-8'))
            assert json_obj["url"] == "http://example.com"

        async for response in async_spider.crawl_url(url, params=params, stream=True, content_type="application/jsonl"):
            handle_json(response)

@pytest.mark.asyncio
async def test_links(async_spider, url, params):
    mock_response = [{"error": None, "status": 200, "url": url}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.links(url, params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_screenshot(async_spider, url, params):
    mock_response = [{"content": "base64_encoded_image", "error": None, "status": 200, "url": url}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.screenshot(url, params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_search(async_spider, params):
    mock_response = [{"content": "result", "error": None, "status": 200, "url": "http://example.com"}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.search("example search query", params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_transform(async_spider, url, params):
    mock_response = {"content": "transformed", "error": None, "status": 200}
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
        async for response in async_spider.transform(transform_data, params=params):
            assert isinstance(response, dict)
            assert 'content' in response
            assert 'error' in response
            assert 'status' in response

@pytest.mark.asyncio
async def test_extract_contacts(async_spider, url, params):
    mock_response = [{"content": "contacts", "error": None, "status": 200, "url": url}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.extract_contacts(url, params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_label(async_spider, url, params):
    mock_response = [{"content": "labels", "error": None, "status": 200, "url": url}]
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.label(url, params=params):
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_get_crawl_state(async_spider, url, params):
    mock_response = {"data": [{"state": "completed", "credits_used": 10}]}
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.get_crawl_state(url, params=params):
            assert isinstance(response, dict)
            assert 'data' in response
            assert isinstance(response['data'], list)

@pytest.mark.asyncio
async def test_get_credits(async_spider):
    mock_response = {"data": [{"credits": 1000}]}
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.get_credits():
            assert isinstance(response, dict)
            assert 'data' in response
            assert isinstance(response['data'], list)

@pytest.mark.asyncio
async def test_data_post(async_spider, url):
    mock_response = None
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        table = "websites"
        post_data: RequestParamsDict = {"url": url}
        async for response in async_spider.data_post(table, post_data):
            assert response is None

@pytest.mark.asyncio
async def test_data_get(async_spider, url, params):
    mock_response = {"data": [{"url": url}]}
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        table = "websites"
        async for response in async_spider.data_get(table, params=params):
            assert isinstance(response['data'], list)

@pytest.mark.asyncio
async def test_query(async_spider, params):
    mock_response = {"data": {"status": 200}}
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.data_get("query", params=params):
            assert isinstance(response['data'], object)

@pytest.mark.asyncio
async def test_data_delete(async_spider, params):
    mock_response = None
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        table = "websites"
        async for response in async_spider.data_delete(table, params=params):
            assert response is None

@pytest.mark.asyncio
async def test_create_signed_url(async_spider):
    mock_response = b"mocked raw data"
    
    async def mock_request(*args, **kwargs):
        yield mock_response

    with patch.object(AsyncSpider, '_request', side_effect=mock_request):
        async for response in async_spider.create_signed_url(params={"domain": "example.com"}):
            assert response == b"mocked raw data"

@pytest.mark.asyncio
async def test_handle_error():
    async_spider = AsyncSpider(api_key="test_api_key")
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 402
    mock_response.json.return_value = {"error": "Payment Required"}
    
    with pytest.raises(Exception, match="Failed to test action. Status code: 402. Error: Payment Required"):
        await async_spider._handle_error(mock_response, "test action")