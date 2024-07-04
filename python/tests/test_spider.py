import pytest, time, os
from spider.spider import Spider
from spider.spider_types import RequestParamsDict
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def spider():
    return Spider()


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
    assert response is not None


def test_crawl_url(spider, url, params):
    response = spider.crawl_url(url, params=params)
    assert response is not None


def test_crawl_url_streaming(spider, url, params):
    def handle_json(json_obj: dict) -> None:
        assert json_obj["url"] is not None

    response = spider.crawl_url(
        url,
        params=params,
        stream=True,
        content_type="application/jsonl",
        callback=handle_json,
    )
    assert response is None


def test_links(spider, url, params):
    response = spider.links(url, params=params)
    assert response is not None


def test_screenshot(spider, url, params):
    response = spider.screenshot(url, params=params)
    assert response is not None


def test_search(spider, params):
    response = spider.search("example search query", params=params)
    assert response is not None


def test_transform(spider, url, params):
    transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
    response = spider.transform(transform_data, params=params)
    assert response is not None


def test_extract_contacts(spider, url, params):
    response = spider.extract_contacts(url, params=params)
    assert response is not None


def test_label(spider, url, params):
    response = spider.label(url, params=params)
    assert response is not None


def test_get_crawl_state(spider, url, params):
    response = spider.get_crawl_state(url, params=params)
    assert response is not None


def test_get_credits(spider):
    response = spider.get_credits()
    assert response is not None


def test_data_post(spider, url):
    table = "websites"
    post_data: RequestParamsDict = {"url": url}
    response = spider.data_post(table, post_data)
    assert response is not None


def test_data_get(spider, url, params):
    table = "websites"
    response = spider.data_get(table, params=params)
    assert response is not None


def test_client_auth(spider):
    spider.init_supabase()
    email_pass = {
        "email": os.getenv("SPIDER_EMAIL"),
        "password": os.getenv("SPIDER_PASSWORD"),
    }
    data = spider.supabase.auth.sign_in_with_password(email_pass)
    assert data, "Failed to authenticate with Supabase"
    data = spider.supabase.auth.sign_out()
    assert data is None


# def test_data_delete(spider, url, params):
#     table = "websites"
#     response = spider.data_delete(table, params=params)
#     assert response is not None
