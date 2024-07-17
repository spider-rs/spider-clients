import asyncio
from spider import AsyncSpider

# Initialize the AsyncSpider with your API key using the env key SPIDER_API_KEY
async_app = AsyncSpider()

crawler_params = {
    'limit': 1,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}



# A callback
def process_json(data: dict) -> None:
    print("Processing data:")
    for key, value in data.items():
        print(f"{key}: {value}")


async def main():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # URL to crawl
    url = 'https://spider.cloud'
        
    # For non-streaming usage:
    print("Non-streaming crawl:")
    async for result in spider.crawl_url(url, params=crawler_params, stream=False):
        print(result)

    
    # For streaming usage with a callback:
    print("\nStreaming crawl with callback:")
    async for _ in spider.crawl_url(url, params=crawler_params, stream=True, callback=process_json):
        pass  # The callback function handles the data processing

    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming crawl without callback:")
    async for chunk in spider.crawl_url(url, params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")

if __name__ == "__main__":
    asyncio.run(main())