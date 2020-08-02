import asyncio
import logging
import re
import urllib.request


async def getLiveVideoId(id):
    if len(id) == 24:
        logging.info('channelId:'+id)
        videoid = await channelId2videoId(id)
        logging.info('videoid:'+str(videoid))
        return videoid
    else:
        return await checkIsLive(id)


async def checkIsLive(videoid):
    fp = urllib.request.urlopen(urllib.request.Request(
        f"https://www.youtube.com/watch?v={videoid}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.24 Safari/537.36'}))
    mybytes = fp.read()
    fp.close()
    htmlsource = mybytes.decode("utf-8")
    if re.search(r'"isLive\\":true,', htmlsource) is None:  # \"isLive\":true,
        return None
    return id


async def channelId2videoId(channelId):
    fp = urllib.request.urlopen(urllib.request.Request(
        f"https://www.youtube.com/channel/{channelId}/live", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.24 Safari/537.36'}))
    mybytes = fp.read()
    fp.close()
    htmlsource = mybytes.decode("utf-8")
    if re.search(r'"isLive\\":true,', htmlsource) is None:  # \"isLive\":true,
        return None
    videoid = re.search(r'(?<="videoId\\":\\")(.*?)(?=\\",)', htmlsource)
    if re.search(r'(?<="videoId\\":\\")(.*?)(?=\\",)', htmlsource) is None:
        logging.warn(r're.search[videoId], htmlsource) is None')
        return None
    return videoid.group()
