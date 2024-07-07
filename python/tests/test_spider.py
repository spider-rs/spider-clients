import pytest
import os
import json
from unittest.mock import patch, MagicMock
from spider.spider import Spider
from spider.spider_types import RequestParamsDict
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def spider():
    return Spider(api_key="test_api_key")

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
    spider = Spider()
    assert spider.api_key == "env_api_key"
    del os.environ["SPIDER_API_KEY"]

def test_init_without_api_key():
    with pytest.raises(ValueError):
        Spider(api_key=None)

@patch('requests.post')
def test_scrape_url(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "mocked data"}
    mock_post.return_value = mock_response

    response = spider.scrape_url(url, params=params)
    assert response == {"data": "mocked data"}
    mock_post.assert_called_once()

@patch('requests.post')
def test_crawl_url(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "mocked data"}
    mock_post.return_value = mock_response

    response = spider.crawl_url(url, params=params)
    assert response == {"data": "mocked data"}
    mock_post.assert_called_once()

@patch('requests.post')
def test_crawl_url_streaming(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b'{"url": "http://example.com"}']
    mock_post.return_value = mock_response

    def handle_json(json_obj):
        assert json_obj["url"] == "http://example.com"

    spider.crawl_url(url, params=params, stream=True, content_type="application/jsonl", callback=handle_json)
    mock_post.assert_called_once()

@patch('requests.post')
def test_links(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"links": ["http://example.com/page1", "http://example.com/page2"]}
    mock_post.return_value = mock_response

    response = spider.links(url, params=params)
    assert "links" in response
    assert len(response["links"]) == 2
    mock_post.assert_called_once()

@patch('requests.post')
def test_screenshot(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"screenshot": "base64_encoded_image"}
    mock_post.return_value = mock_response

    response = spider.screenshot(url, params=params)
    assert "screenshot" in response
    mock_post.assert_called_once()

@patch('requests.post')
def test_search(mock_post, spider, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [{"url": "http://example.com", "title": "Example"}]}
    mock_post.return_value = mock_response

    response = spider.search("example search query", params=params)
    assert "results" in response
    assert len(response["results"]) > 0
    mock_post.assert_called_once()

@patch('requests.post')
def test_transform(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"transformed": "# Example"}
    mock_post.return_value = mock_response

    transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
    response = spider.transform(transform_data, params=params)
    assert "transformed" in response
    mock_post.assert_called_once()

@patch('requests.post')
def test_extract_contacts(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"contacts": [{"email": "test@example.com"}]}
    mock_post.return_value = mock_response

    response = spider.extract_contacts(url, params=params)
    assert "contacts" in response
    assert len(response["contacts"]) > 0
    mock_post.assert_called_once()

@patch('requests.post')
def test_label(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"labels": ["technology", "news"]}
    mock_post.return_value = mock_response

    response = spider.label(url, params=params)
    assert "labels" in response
    assert len(response["labels"]) > 0
    mock_post.assert_called_once()

@patch('requests.post')
def test_get_crawl_state(mock_post, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"state": "completed", "credits_used": 10}
    mock_post.return_value = mock_response

    response = spider.get_crawl_state(url, params=params)
    assert "state" in response
    assert "credits_used" in response
    mock_post.assert_called_once()

@patch('requests.get')
def test_get_credits(mock_get, spider):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"credits": 1000}
    mock_get.return_value = mock_response

    response = spider.get_credits()
    assert "credits" in response
    mock_get.assert_called_once()

@patch('requests.post')
def test_data_post(mock_post, spider, url):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "123"}
    mock_post.return_value = mock_response

    table = "websites"
    post_data: RequestParamsDict = {"url": url}
    response = spider.data_post(table, post_data)
    assert "id" in response
    mock_post.assert_called_once()

@patch('requests.get')
def test_data_get(mock_get, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"url": url}]}
    mock_get.return_value = mock_response

    table = "websites"
    response = spider.data_get(table, params=params)
    assert "data" in response
    assert len(response["data"]) > 0
    mock_get.assert_called_once()

@patch('requests.delete')
def test_data_delete(mock_delete, spider, url, params):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"deleted": True}
    mock_delete.return_value = mock_response

    table = "websites"
    response = spider.data_delete(table, params=params)
    assert "deleted" in response
    assert response["deleted"] is True
    mock_delete.assert_called_once()

@patch('requests.get')
def test_create_signed_url(mock_get, spider):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raw = b"mocked raw data"
    mock_get.return_value = mock_response

    response = spider.create_signed_url(domain="example.com", options={"page": 1, "limit": 10})
    assert response == b"mocked raw data"
    mock_get.assert_called_once()

def test_supabase_init(spider):
    with patch('spider.supabase_client.Supabase._initialize_client') as mock_init:
        spider.init_supabase()
        mock_init.assert_called_once()

def test_supabase_get_client_not_initialized(spider):
    with pytest.raises(Exception, match="Supabase client is not initialized"):
        spider.supabase

def test_stream_reader():
    spider = Spider(api_key="test_api_key")
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b'{"key": "value"}\n', b'{"key2": "value2"}\n']
    
    callback_data = []
    def callback(json_obj):
        callback_data.append(json_obj)
    
    spider.stream_reader(mock_response, callback)
    assert len(callback_data) == 2
    assert callback_data[0] == {"key": "value"}
    assert callback_data[1] == {"key2": "value2"}

def test_handle_error():
    spider = Spider(api_key="test_api_key")
    mock_response = MagicMock()
    mock_response.status_code = 402
    mock_response.json.return_value = {"error": "Payment Required"}
    
    with pytest.raises(Exception, match="Failed to test action. Status code: 402. Error: Payment Required"):
        spider._handle_error(mock_response, "test action")

