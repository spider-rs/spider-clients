# Getting started

To use the python SDK you will (of course) have to install it :)

```bash
pip install spider-client
```

[Here](https://pypi.org/project/spider-client/) is the link to the package on PyPi.

## Setting & Getting Api Key

To use the SDK you will need an API key. You can get one by signing up on [spider.cloud](https://spider.cloud?ref=python-sdk-book).

Then you need to set the API key in your environment variables.

```bash
export SPIDER_API_KEY=your_api_key
```

if you don't want to set the API key in your environment variables you can pass it as an argument to the `Spider` class.

```python
from spider import Spider
app = Spider(api_key='your_api_key')
```

We recommend setting the API key in your environment variables.
