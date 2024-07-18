import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from spider import AsyncSpider
from spider.spider_types import RequestParamsDict
import aiohttp
from aiohttp import ClientResponse

pytest_plugins = ('pytest_asyncio',)

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
    mock_response.json = AsyncMock(return_value=[{"content": "data", "error": None, "status": 200, "url": url}])
    
    with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
        mock_api_post.return_value = [mock_response]
        print(dir(async_spider.scrape_url(url, params=params)))
        responses = [r async for r in async_spider.scrape_url(url, params=params)]
        response = responses[0]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

@pytest.mark.skip
@pytest.mark.asyncio
async def test_crawl_url(async_spider, url, params):
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[{"content": "data", "error": None, "status": 200, "url": url}])

    with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
        mock_api_post.return_value = [mock_response]
        responses = [r async for r in async_spider.crawl_url(url, params=params)]
        response = responses[0]
        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)
        assert 'content' in response[0]
        assert 'error' in response[0]
        assert 'status' in response[0]
        assert 'url' in response[0]

# @pytest.mark.asyncio
# async def test_links(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value=[{"error": None, "status": 200, "url": url}])

#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.links(url, params=params)]
#         response = responses[0]
#         assert isinstance(response, list)
#         assert len(response) > 0
#         assert isinstance(response[0], dict)
#         assert 'error' in response[0]
#         assert 'status' in response[0]
#         assert 'url' in response[0]

# @pytest.mark.asyncio
# async def test_screenshot(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value=[{"content": "base64_encoded_image", "error": None, "status": 200, "url": url}])

#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.screenshot(url, params=params)]
#         response = responses[0]
#         assert isinstance(response, list)
#         assert len(response) > 0
#         assert isinstance(response[0], dict)
#         assert 'content' in response[0]
#         assert 'error' in response[0]
#         assert 'status' in response[0]
#         assert 'url' in response[0]

# @pytest.mark.asyncio
# async def test_search(async_spider, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value=[{"content": "result", "error": None, "status": 200, "url": "http://example.com"}])

#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.search("example search query", params=params)]
#         response = responses[0]
#         assert isinstance(response, list)
#         assert len(response) > 0
#         assert isinstance(response[0], dict)
#         assert 'content' in response[0]
#         assert 'error' in response[0]
#         assert 'status' in response[0]
#         assert 'url' in response[0]

# @pytest.mark.asyncio
# async def test_transform(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value={"content": "transformed", "error": None, "status": 200})

#     transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.transform(transform_data, params=params)]
#         response = responses[0]
#         assert isinstance(response, dict)
#         assert 'content' in response
#         assert 'error' in response
#         assert 'status' in response

# @pytest.mark.asyncio
# async def test_extract_contacts(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value=[{"content": "contacts", "error": None, "status": 200, "url": url}])

#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.extract_contacts(url, params=params)]
#         response = responses[0]
#         assert isinstance(response, list)
#         assert len(response) > 0
#         assert isinstance(response[0], dict)
#         assert 'content' in response[0]
#         assert 'error' in response[0]
#         assert 'status' in response[0]
#         assert 'url' in response[0]

# @pytest.mark.asyncio
# async def test_label(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value=[{"content": "labels", "error": None, "status": 200, "url": url}])

#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.label(url, params=params)]
#         response = responses[0]
#         assert isinstance(response, list)
#         assert len(response) > 0
#         assert isinstance(response[0], dict)
#         assert 'content' in response[0]
#         assert 'error' in response[0]
#         assert 'status' in response[0]
#         assert 'url' in response[0]

# @pytest.mark.asyncio
# async def test_get_crawl_state(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value={"data": [{"state": "completed", "credits_used": 10}]})

#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.get_crawl_state(url, params=params)]
#         response = responses[0]
#         assert isinstance(response, dict)
#         assert 'data' in response
#         assert isinstance(response['data'], list)

# @pytest.mark.asyncio
# async def test_get_credits(async_spider):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value={"data": [{"credits": 1000}]})

#     with patch.object(AsyncSpider, 'api_get', new_callable=AsyncMock) as mock_api_get:
#         mock_api_get.return_value = [mock_response]
#         responses = [r async for r in async_spider.get_credits()]
#         response = responses[0]
#         assert isinstance(response, dict)
#         assert 'data' in response
#         assert isinstance(response['data'], list)

# @pytest.mark.asyncio
# async def test_data_post(async_spider, url):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 204

#     table = "websites"
#     post_data: RequestParamsDict = {"url": url}
#     with patch.object(AsyncSpider, 'api_post', new_callable=AsyncMock) as mock_api_post:
#         mock_api_post.return_value = [mock_response]
#         responses = [r async for r in async_spider.data_post(table, post_data)]
#         response = responses[0]
#         assert response is not None

# @pytest.mark.asyncio
# async def test_data_get(async_spider, url, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value={"data": [{"url": url}]})

#     table = "websites"
#     with patch.object(AsyncSpider, 'api_get', new_callable=AsyncMock) as mock_api_get:
#         mock_api_get.return_value = [mock_response]
#         responses = [r async for r in async_spider.data_get(table, params=params)]
#         response = responses[0]
#         assert isinstance(response, dict)
#         assert 'data' in response
#         assert isinstance(response['data'], list)

# @pytest.mark.asyncio
# async def test_data_delete(async_spider, params):
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 204

#     table = "websites"
#     with patch.object(AsyncSpider, 'api_delete', new_callable=AsyncMock) as mock_api_delete:
#         mock_api_delete.return_value = [mock_response]
#         responses = [r async for r in async_spider.data_delete(table, params=params)]
#         response = responses[0]
#         assert response is not None

# @pytest.mark.asyncio
# async def test_handle_error():
#     mock_response = MagicMock(spec=ClientResponse)
#     mock_response.status = 402
#     mock_response.headers = {'Content-Type': 'application/json'}
#     mock_response.json = AsyncMock(return_value={"error": "Payment Required"})
    
#     async_spider = AsyncSpider(api_key="test_api_key")
#     with pytest.raises(Exception, match="Failed to test action. Status code: 402. Error: Payment Required"):
#         await async_spider._handle_error(mock_response, "test action")
