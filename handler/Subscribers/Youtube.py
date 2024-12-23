from xml.etree.ElementTree import ElementTree
from handler.Subscriber import WebSubSubscriber
from models.SubscriptionModels import Feed
from models.TaskModels import NewDownloadTask
import hmac
import hashlib


class YoutubeSubscriber(WebSubSubscriber):

    async def parse_xml_to_feed(self, xml: ElementTree) -> Feed:
        namespace = {
            'yt': "http://www.youtube.com/xml/schemas/2015",
            '': "http://www.w3.org/2005/Atom"
        }
        entry = xml.find('entry', namespace)
        author = entry.find('author', namespace)
        return Feed(video_id=entry.find('yt:videoId', namespace).text,
                    video_title=entry.find('title', namespace).text,
                    video_url=entry.find("link[@rel='alternate']", namespace).get("href"),
                    channel_id=entry.find('yt:channelId', namespace).text,
                    channel_title=author.find('name', namespace).text,
                    channel_url=author.find('uri', namespace).text,
                    site="youtube")

    async def parse_feed_to_download_task(self, feed: Feed) -> NewDownloadTask:
        return NewDownloadTask(
            name=feed.video_title,
            url=feed.video_url,
            site=feed.site
        )

    async def compare_signature(self, secret: str, body: bytes, signature: str) -> bool:
        calculated_signature = hmac.new(secret.encode(), body, hashlib.sha1).hexdigest()
        return calculated_signature == signature
