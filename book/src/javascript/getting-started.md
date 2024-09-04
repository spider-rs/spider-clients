# Getting started

To be able to use the javascript SDK you will (of course) have to install it. You can do so with your package manager of choice.

```bash
npm install @spider-cloud/spider-client
```

```bash
yarn add @spider-cloud/spider-client
```

[Here](https://www.npmjs.com/package/@spider-cloud/spider-client) is the link to the package on npm.

## Setting & Getting Api Key

To use the SDK you will need an API key. You can get one by signing up on [spider.cloud](https://spider.cloud?ref=javascript-sdk-book).

Then you need to set the API key in your environment variables.

```bash
export SPIDER_API_KEY=your_api_key
```

if you don't want to set the API key in your environment variables you can pass it as an argument to the `Spider` class.

```javascript
import { Spider } from "@spider-cloud/spider-client";
```

We recommend setting the API key in your environment variables.
