import asyncio
import logging
import re
import aiohttp

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.24 Safari/537.36'}


async def getLiveVideoId(id):
    if len(id) == 24:
        logging.debug('channelId:'+id)
        videoid = await channelId2videoId(id)
        logging.debug('videoid:'+str(videoid))
        return videoid
    else:
        return await checkIsLive(id)


async def checkIsLive(videoid):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.youtube.com/watch?v={videoid}", headers=headers) as r:
            if r.status == 200:
                htmlsource = await r.text()
                if re.search(r'"isLive\\":true,', htmlsource) is None:  # \"isLive\":true,
                    return None
                return id
            else:
                logging.error('checkIsLive.status:'+r.status)
                return None


async def channelId2videoId(channelId):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.youtube.com/channel/{channelId}/live", headers=headers) as r:
            if r.status == 200:
                htmlsource = await r.text()
                if re.search(r'"isLive\\":true,', htmlsource) is None:  # \"isLive\":true,
                    return None
                videoid = re.search(
                    r'(?<="videoId\\":\\")(.*?)(?=\\",)', htmlsource)
                if re.search(r'(?<="videoId\\":\\")(.*?)(?=\\",)', htmlsource) is None:
                    logging.warn(r're.search[videoId], htmlsource) is None')
                    return None
                return videoid.group()
            else:
                logging.error('channelId2videoId.status:'+r.status)
                return None
