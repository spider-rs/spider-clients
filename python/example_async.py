import asyncio
from spider import AsyncSpider

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


async def crawl_url():
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


asyncio.run(crawl_url())


async def scrape_url():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # URL to crawl
    url = 'https://spider.cloud'
        
    # For non-streaming usage:
    print("Non-streaming scrape:")
    async for result in spider.scrape_url(url, params=crawler_params, stream=False):
        print(result)

    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming scrape without callback:")
    async for chunk in spider.scrape_url(url, params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")


async def links():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # URL to crawl
    url = 'https://spider.cloud'
        
    # For non-streaming usage:
    print("Non-streaming links:")
    async for result in spider.links(url, params=crawler_params, stream=False):
        print(result)

    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming links without callback:")
    async for chunk in spider.links(url, params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")


async def screenshot():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # URL to crawl
    url = 'https://spider.cloud'
        
    # For non-streaming usage:
    print("Non-streaming screenshot:")
    async for result in spider.screenshot(url, params=crawler_params, stream=False):
        print(result)

    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming screenshot without callback:")
    async for chunk in spider.screenshot(url, params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")


async def search():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # Search term
    q = "what is spider cloud?"
    
    # For non-streaming usage:
    print("Non-streaming search:")
    async for result in spider.search(q=q, params=crawler_params, stream=False):
        print(result)

    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming search without callback:")
    async for chunk in spider.search(q=q,params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")


async def transform():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # URL to crawl
    url = 'https://spider.cloud'
    
    # Get html
    async for result in spider.crawl_url(url=url, params=crawler_params, stream=False):
        data = result

    data[0]['html'] = data[0]['content'] # ! Transform endpoint expects html, not content
    print("Non-streaming transform:")
    async for result in spider.transform(data=data, params=crawler_params, stream=False):
        print(result)
        
    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming transform without callback:")
    async for chunk in spider.transform(data=data,params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")


async def contacts():
    # Initialize the AsyncSpider
    spider = AsyncSpider()

    # URL to crawl
    url = 'https://spider.cloud'
        
    # For non-streaming usage:
    print("Non-streaming contacts:")
    async for result in spider.extract_contacts(url, params=crawler_params, stream=False):
        print(result)

    # For streaming usage without a callback (just prints the response headers):
    print("\nStreaming contacts without callback:")
    async for chunk in spider.extract_contacts(url, params=crawler_params, stream=True):
        print(f"Received chunk: {chunk}")
        

async def credits():
    # Initialize the AsyncSpider
    spider = AsyncSpider()
    
    async for result in spider.get_credits():
        print(result)


async def data_get():
    spider = AsyncSpider()
    
    async for result in spider.data_get("websites", params=crawler_params):
        print(result)
        

async def data_delete():
    spider = AsyncSpider()
    
    async for result in spider.data_delete("websites", params=crawler_params):
        print(result)
        
if __name__ == "__main__":
    asyncio.run(crawl_url())
    asyncio.run(scrape_url())
    asyncio.run(links())
    asyncio.run(screenshot())
    asyncio.run(search())
    asyncio.run(transform())
    asyncio.run(contacts())
    asyncio.run(credits())    
    asyncio.run(data_get())    
    asyncio.run(data_delete())    
    
    
    