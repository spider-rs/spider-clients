import pytest
import os
import logging
from spider.spider import Spider
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def spider():
    api_key = os.getenv("SPIDER_API_KEY")
    if not api_key:
        pytest.skip("SPIDER_API_KEY not set in .env file")
    return Spider(api_key=api_key)

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

def test_scrape_url(spider, url, params):
    response = spider.scrape_url(url, params=params)
    logger.info(f"Scrape URL response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'content' in response[0]
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_crawl_url(spider, url, params):
    response = spider.crawl_url(url, params=params)
    logger.info(f"Crawl URL response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'content' in response[0]
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_links(spider, url, params):
    response = spider.links(url, params=params)
    logger.info(f"Links response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_screenshot(spider, url, params):
    response = spider.screenshot(url, params=params)
    logger.info(f"Screenshot response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'content' in response[0]
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_search(spider, params):
    response = spider.search("example search query", params=params)
    logger.info(f"Search response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'content' in response[0]
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_transform(spider, url, params):
    transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
    response = spider.transform(transform_data, params=params)
    logger.info(f"Transform response: {response}")
    assert isinstance(response, dict)
    assert 'content' in response
    assert 'error' in response
    assert 'status' in response

def test_extract_contacts(spider, url, params):
    response = spider.extract_contacts(url, params=params)
    logger.info(f"Extract contacts response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'content' in response[0]
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_label(spider, url, params):
    response = spider.label(url, params=params)
    logger.info(f"Label response: {response}")
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], dict)
    assert 'content' in response[0]
    assert 'error' in response[0]
    assert 'status' in response[0]
    assert 'url' in response[0]

def test_get_crawl_state(spider, url, params):
    response = spider.get_crawl_state(url, params=params)
    logger.info(f"Get crawl state response: {response}")
    assert isinstance(response, dict)
    assert 'data' in response
    assert isinstance(response['data'], list)

def test_get_credits(spider):
    response = spider.get_credits()
    logger.info(f"Get credits response: {response}")
    assert isinstance(response, dict)
    assert 'data' in response
    assert isinstance(response['data'], list)

def test_data_post(spider, url):
    table = "websites"
    post_data = {"url": url}
    response = spider.data_post(table, post_data)
    logger.info(f"Data post response: {response}")
    assert isinstance(response['data'], dict)
    assert response['data']['url'] == url
    assert response['data']['domain'] == url.replace("http://", "").replace("https://", "")
    assert response['error'] == None

# TODO: 500 error. 
# def test_data_get(spider, params):
#     table = "websites"
#     response = spider.data_get(table, params=params)
#     logger.info(f"Data get response: {response}")
#     assert isinstance(response['data'], list)

def test_data_delete(spider, params):
    table = "websites"
    response = spider.data_delete(table, params=params)
    logger.info(f"Data delete response: {response}")
    assert response['message'] == 'ok'

# TODO: 500 error. 
# def test_create_signed_url(spider):
#     response = spider.create_signed_url(domain="example.com", options={"page": 1, "limit": 10})
#     logger.info(f"Create signed URL response: {response}")
#     assert isinstance(response, bytes)
