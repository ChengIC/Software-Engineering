"""
This code is using the async approach, while waiting for one Reddit API response,
it can start requesting another, all managed by a single thread and event loop.

"""

import signal  
import sys  
import asyncio  
import aiohttp  
import json

async def get_json(client, url):  
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()

async def get_reddit_top(subreddit, client):  
    data1 = await get_json(client, 'https://www.reddit.com/r/' + subreddit + '/top.json?sort=top&t=day&limit=5')

    j = json.loads(data1.decode('utf-8'))
    for i in j['data']['children']:
        score = i['data']['score']
        title = i['data']['title']
        link = i['data']['url']
        print(str(score) + ': ' + title + ' (' + link + ')')

    print('DONE:', subreddit + '\n')

async def main():
    async with aiohttp.ClientSession() as client:
        tasks = [
            get_reddit_top('python', client),
            get_reddit_top('programming', client),
            get_reddit_top('compsci', client)
        ]
        await asyncio.gather(*tasks)

def signal_handler(signal, frame):
    for task in asyncio.all_tasks():
        task.cancel()
    asyncio.get_event_loop().stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()