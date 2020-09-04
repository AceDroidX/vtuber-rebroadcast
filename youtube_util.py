import asyncio
import logging
import re
import aiohttp

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.24 Safari/537.36'}


async def getLiveVideoId(id):
    logger = logging.getLogger('youtube_util')
    if len(id) == 24:
        logger.debug('channelId:'+id)
        videoid = await channelId2videoId(id)
        logger.debug('videoid:'+str(videoid))
        return videoid
    else:
        return await checkIsLive(id)


async def checkIsLive(videoid):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.youtube.com/watch?v={videoid}", headers=headers) as r:
            if r.status == 200:
                htmlsource = await r.text()
                videoid = re.search(r'"isLive\\":true,', htmlsource)
                if videoid is None:  # \"isLive\":true,
                    return {'status': 'None'}
                return {'videoid': videoid.group(), 'status': 'OK'}
            else:
                logging.getLogger('youtube_util').error(
                    'checkIsLive.status:'+r.status)
                return {'status': 'None'}


async def channelId2videoId(channelId):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.youtube.com/channel/{channelId}/live", headers=headers) as r:
            if r.status == 200:
                htmlsource = await r.text()
                if re.search(r'"isLive\\":true,', htmlsource) is None:  # \"isLive\":true,
                    # debug
                    with open(f'test-{channelId}.html', 'w') as f:
                        f.write(htmlsource)
                    #
                    scheduledStartTime = re.search(
                        r'(?<="scheduledStartTime\\":\\")(.*?)(?=\\",)', htmlsource)
                    if scheduledStartTime == None:
                        scheduledStartTime = 'None'
                    else:
                        scheduledStartTime = int(scheduledStartTime.group())
                    status = re.search(
                        r'(?<="status\\":\\")(.*?)(?=\\",)', htmlsource)
                    if status is None:
                        return {'status': 'None'}
                    elif status.group() == 'LIVE_STREAM_OFFLINE':
                        return {'videoid': re.search(
                            r'(?<="videoId\\":\\")(.*?)(?=\\",)', htmlsource).group(), 'status': 'LIVE_STREAM_OFFLINE', 'scheduledStartTime': scheduledStartTime}
                    elif status.group() == 'OK':  # 注：这是正常情况，返回的是频道主页界面
                        return {'status': 'None'}
                    else:
                        logging.getLogger('youtube_util').error(
                            f'channelId2videoId:[{channelId}]未知状态:{status.group()}')
                        return {'status': 'None'}
                videoid = re.search(
                    r'(?<="videoId\\":\\")(.*?)(?=\\",)', htmlsource)
                return {'videoid': videoid.group(), 'status': 'OK'}
            else:
                logging.getLogger('youtube_util').error(
                    f'channelId2videoId.status:{r.status}')
                return {'status': 'None'}
