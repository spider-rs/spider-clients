# Simple Example

This is a simple example of what you can do with the `spider-client` library.

## Installation

To install the library, you can use `pip` for Python or `npm` (make sure to have [node](https://nodejs.org/en) installed) for JavaScript.:

```bash
# for python
pip install spider-client
```

```bash
# for javascript
npm install @spider-cloud/spider-client
```

## Usage

Here is an example of how you can use the library, make sure to replace `your_api_key` with your actual API key which you can get from the [spider.cloud](https://spider.cloud) website.

```python
from spider import Spider

app = Spider(api_key='your_api_key')
url = 'https://spider.cloud'
scraped_data = app.scrape_url(url)
```

```javascript
import { Spider } from "@spider-cloud/spider-client";

const app = new Spider({ apiKey: "your-api-key" });
const url = "https://spider.cloud";
const scrapedData = await app.scrapeUrl(url);
console.log(scrapedData);
```
