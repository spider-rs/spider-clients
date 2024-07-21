import pytest
import os
import logging
from spider.async_spider import AsyncSpider
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def api_key():
    api_key = os.getenv("SPIDER_API_KEY")
    if not api_key:
        pytest.skip("SPIDER_API_KEY not set in .env file")
    return api_key

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
async def test_scrape_url(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.scrape_url(url, params=params):
            print(type(response))
            logger.info(f"Scrape URL response: {response}")
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_crawl_url(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.crawl_url(url, params=params):
            logger.info(f"Crawl URL response: {response}")
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

# TODO "Credits or a valid subscription required to use the API"?
# @pytest.mark.asyncio
# async def test_crawl_url_streaming(url, params):
#     async with AsyncSpider(api_key=api_key) as spider:
#         async for response in spider.crawl_url(url, params=params, stream=True):
#             print(response)
#             json_obj = json.loads(response.decode('utf-8'))
#             assert json_obj["url"] == "http://example.com"

@pytest.mark.asyncio
async def test_links(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.links(url, params=params):
            logger.info(f"Links response: {response}")
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_screenshot(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.screenshot(url, params=params):
            logger.info(f"Screenshot response: {response}")
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_search(api_key, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.search("example search query", params=params):
            logger.info(f"Search response: {response}")
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_transform(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
        async for response in spider.transform(transform_data, params=params):
            logger.info(f"Transform response: {response}")
            assert isinstance(response, dict)
            assert 'content' in response
            assert 'error' in response
            assert 'status' in response

@pytest.mark.asyncio
async def test_extract_contacts(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.extract_contacts(url, params=params):
            logger.info(f"Extract contacts response: {response}")
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_label(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.label(url, params=params):
            logger.info(f"Label response: {response}")
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], dict)
            assert 'content' in response[0]
            assert 'error' in response[0]
            assert 'status' in response[0]
            assert 'url' in response[0]

@pytest.mark.asyncio
async def test_get_crawl_state(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.get_crawl_state(url, params=params):
            logger.info(f"Get crawl state response: {response}")
            assert isinstance(response, dict)
            assert 'data' in response
            assert isinstance(response['data'], list)

@pytest.mark.asyncio
async def test_get_credits(api_key):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.get_credits():
            logger.info(f"Get credits response: {response}")
            assert isinstance(response, dict)
            assert 'data' in response
            assert isinstance(response['data'], list)

@pytest.mark.asyncio
async def test_data_post(api_key, url):
    async with AsyncSpider(api_key=api_key) as spider:
        table = "websites"
        post_data = {"url": url}
        async for response in spider.data_post(table, post_data):
            logger.info(f"Data post response: {response}")
            assert 200 <= response['status'] < 300
            assert response['data']['created_at'] is not None

# TODO 500 error
# @pytest.mark.asyncio
# async def test_data_get(api_key, url, params):
#     async with AsyncSpider(api_key=api_key) as spider:
#         table = "websites"
#         async for response in spider.data_get(table, params=params):
#             logger.info(f"Data get response: {response}")
#             print(response)
#             assert isinstance(response['data'], list)

@pytest.mark.asyncio
async def test_data_delete(api_key, url, params):
    async with AsyncSpider(api_key=api_key) as spider:
        table = "websites"
        async for response in spider.data_delete(table, params=params):
            logger.info(f"Data delete response: {response}")
            print(response)
            assert response['message'] == 'ok'

@pytest.mark.asyncio
async def test_create_signed_url(api_key):
    async with AsyncSpider(api_key=api_key) as spider:
        async for response in spider.create_signed_url(params={"domain": "example.com"}):
            logger.info(f"Create signed URL response: {response}")
            assert isinstance(response, bytes)