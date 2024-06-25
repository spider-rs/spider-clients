from spider.spider import Spider, RequestParamsDict

def main():
    spider = Spider()

    # Test scrape_url method
    url = "http://example.com"
    params: RequestParamsDict = {
        "limit": 1,
        "return_format": "html2text",
        "depth": 2,
        "cache": True,
    }
    try:
        response = spider.scrape_url(url, params=params)
        print("scrape_url response:", response)
    except Exception as e:
        print("scrape_url error:", e)

    # Test crawl_url method
    try:
        response = spider.crawl_url(url, params=params)
        print("crawl_url response:", response)
    except Exception as e:
        print("crawl_url error:", e)

    # Test links method
    try:
        response = spider.links(url, params=params)
        print("links response:", response)
    except Exception as e:
        print("links error:", e)

    # Test screenshot method
    try:
        response = spider.screenshot(url, params=params)
        print("screenshot response:", response)
    except Exception as e:
        print("screenshot error:", e)

    # Test search method
    try:
        response = spider.search("example search query", params=params)
        print("search response:", response)
    except Exception as e:
        print("search error:", e)

    # Test transform method
    try:
        transform_data = [{"html": "<html><body>Example</body></html>", "url": url}]
        response = spider.transform(transform_data, params=params)
        print("transform response:", response)
    except Exception as e:
        print("transform error:", e)

    # Test extract_contacts method
    try:
        response = spider.extract_contacts(url, params=params)
        print("extract_contacts response:", response)
    except Exception as e:
        print("extract_contacts error:", e)

    # Test label method
    try:
        response = spider.label(url, params=params)
        print("label response:", response)
    except Exception as e:
        print("label error:", e)

    # Test get_crawl_state method
    try:
        response = spider.get_crawl_state(url, params=params)
        print("get_crawl_state response:", response)
    except Exception as e:
        print("get_crawl_state error:", e)

    # Test get_credits method
    try:
        response = spider.get_credits()
        print("get_credits response:", response)
    except Exception as e:
        print("get_credits error:", e)

    # Test data_post method
    try:
        table = "example_table"
        post_data: RequestParamsDict = {"url": url}
        response = spider.data_post(table, post_data)
        print("data_post response:", response)
    except Exception as e:
        print("data_post error:", e)

    # Test data_get method
    try:
        response = spider.data_get(table, params=params)
        print("data_get response:", response)
    except Exception as e:
        print("data_get error:", e)

    # Test data_delete method
    try:
        response = spider.data_delete(table, params=params)
        print("data_delete response:", response)
    except Exception as e:
        print("data_delete error:", e)

if __name__ == "__main__":
    main()
