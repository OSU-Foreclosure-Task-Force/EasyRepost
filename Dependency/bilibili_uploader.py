import os
import re
import math
import base64
import requests
import json
import pysrt
import time
from requests.adapters import HTTPAdapter
from concurrent import futures
from event.Event import Event

class UploadChunkPara:
    @classmethod
    def initClass(cls, upload_session, filePath, total_chunks, uploadId, filesize, uploadUrl):
        cls.upload_session = upload_session
        cls.filePath = filePath
        cls.total_chunks = total_chunks
        cls.uploadId = uploadId
        cls.filesize = filesize
        cls.uploadUrl = uploadUrl

class BilibiliUploader:
    def __init__(self,
                 uid: int,
                 type: int,
                 cookie:str,
                 max_retry: int,
                 max_workers: int,
                 chunk_size: int,
                 profile: str,
                 cdn: str,
                 notification_event: Event,
                 pipe = None):
        self.uid = uid
        self.type = type
        self.MAX_RETRYS = max_retry
        self.MAX_WORKERS = max_workers
        self.CHUNK_SIZE = chunk_size
        self.profile = profile
        self.cdn = cdn
        self.csrf = re.search('bili_jct=(.*?);', cookie + ';').group(1)
        self.mid = re.search('DedeUserID=(.*?);', cookie + ';').group(1)
        self.session = requests.session()
        self.session.mount('https://', HTTPAdapter(max_retries=self.MAX_RETRYS))
        self.session.headers['cookie'] = cookie
        def cookie_to_dic(cookie):
            return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}
        self.cookiedic = cookie_to_dic(cookie)
        self.session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        self.session.headers['Referer'] = 'https://space.bilibili.com/{mid}/#!/'.format(mid=self.mid)
        self._notification_event: Event = notification_event
        self._pipe = pipe

    def _pipe_send(self, payload):
        if self._pipe is None:
            return
        self._pipe.send(payload)

    def _upload(self, filepath):
        """执行上传文件操作"""
        if not os.path.isfile(filepath):
            raise Exception('FILE NOT EXISTS: {}'.format(filepath))

        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        # 1.获取本次上传所需信息
        preupload_url = 'https://member.bilibili.com/preupload'
        params = {
            'os': 'upos',
            'r': 'upos',
            'ssl': '0',
            'name': filename,
            'size': filesize,
            'upcdn': self.cdn,
            'profile': self.profile,
        }
        response = self.session.get(preupload_url, params=params)
        try:
            upload_info = response.json()
        except:
            self._pipe_send(RuntimeError("上传获取 response 失败，登录 cookie 可能已经失效"))

        # 本次上传bilibili端文件名
        upload_info['bili_filename'] = upload_info['upos_uri'].split('/')[-1].split('.')[0]
        # 本次上传url
        endpoint = 'http:%s/' % upload_info['endpoint']
        upload_url = re.sub(r'^upos://', endpoint, upload_info['upos_uri'])
        print('UPLOAD URL: {}'.format(upload_url))
        # 本次上传session
        upload_session = requests.session()
        upload_session.mount('http://', HTTPAdapter(max_retries=self.MAX_RETRYS))
        upload_session.headers['X-Upos-Auth'] = upload_info['auth']

        # 2.获取本次上传的upload_id
        response = upload_session.post(upload_url + '?uploads&output=json')
        upload_info['upload_id'] = response.json()['upload_id']

        # 3.分块上传文件
        total_chunks = math.ceil(filesize * 1.0 / self.CHUNK_SIZE)
        parts_info = {'parts': [{'partNumber': i + 1, 'eTag': 'etag'} for i in range(total_chunks)]}

        print("UPLOAD VIDEO...")

        UploadChunkPara.initClass(upload_session, filepath, total_chunks, upload_info['upload_id'], filesize,
                                  upload_url)
        self._uploadChunkPara = UploadChunkPara()
        chunkNos = list(range(total_chunks))

        with futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            executor.map(self.uploadChunk, chunkNos)

        # 4.标记本次上传完成
        params = {
            'output': 'json',
            'name': filename,
            'profile': self.profile,
            'uploadId': upload_info['upload_id'],
            'biz_id': upload_info['biz_id']
        }
        response = upload_session.post(upload_url, params=params, data=parts_info)
        print('UPLOAD INFO: {}'.format(upload_info))
        print("UPLOADRESP", response.json())
        success = 'OK' in response.json()
        print(response.json().keys())
        print(f"Upload success {success}")
        return upload_info, success

    def _cover_up(self, image_path):
        """上传图片并获取图片链接"""
        if not os.path.isfile(image_path):
            return ''
        fp = open(image_path, 'rb')
        encode_data = base64.b64encode(fp.read())
        url='https://member.bilibili.com/x/vu/web/cover/up'
        data={
            'cover': b'data:image/jpeg;base64,' + encode_data,
            'csrf': self.csrf,
        }
        response = self.session.post(url, data=data)
        return response.json()['data']['url']

    def uploadChunk(self, chunkNo):
        print("start upload chunk {} ... (total {})".format(chunkNo, self._uploadChunkPara.total_chunks))
        chunkNo = chunkNo
        offset = self.CHUNK_SIZE * chunkNo

        with open(self._uploadChunkPara.filePath, "rb") as fp:
            fp.seek(self.CHUNK_SIZE * chunkNo)
            blob = fp.read(self.CHUNK_SIZE)

        params = {
            'partNumber': chunkNo + 1,
            'uploadId': self._uploadChunkPara.uploadId,
            'chunk': chunkNo,
            'chunks': self._uploadChunkPara.total_chunks,
            'size': len(blob),
            'start': offset,
            'end': offset + len(blob),
            'total': self._uploadChunkPara.filesize,
        }
        response = self._uploadChunkPara.upload_session.put(self._uploadChunkPara.uploadUrl, params=params, data=blob,
                                                            timeout=30)

        if response.getcode() != 200:
            print('chunk {} failed, code {} retry...'.format(chunkNo, response.getcode()))
            self.uploadChunk(chunkNo)

        print('chunk {} uploaded'.format(chunkNo))

        return response

    def _upload_all(self, filepath, bucket):
        upload_info, success = self._upload(filepath)
        if not upload_info:
            return
        if bucket:
            self._notification_event.emit("本次投稿将上传防撞桶")
            bucket_upload_info, success_bucket = self._upload(bucket)
            if not bucket_upload_info:
                return
            self._notification_event.emit("防撞桶已上传")
            success = success and success_bucket
        return upload_info, bucket_upload_info if bucket else None, success

    def _upload_retry(self, filepath, bucket, source):
        retries = [0, 1, 2, 4, 8, 16]
        retry_times = len(retries)
        now_times = 0
        upload_info, bucket_upload_info, success = self._upload_all(filepath, bucket)
        while not success:
            if now_times >= retry_times:
                self._pipe_send(RuntimeError(f"重新上传失败，请重新手动上传\n"
                              f"链接：{source}"))
            hour = retries[now_times]
            self._pipe_send(RuntimeError(f"上传出现错误，{hour} 小时后重新上传"))
            time.sleep(hour*60*60)
            upload_info, bucket_upload_info, success = self._upload_all(filepath, bucket)
            now_times += 1
        return upload_info, bucket_upload_info


    def upload(self, filepath, title, tid, tag='', desc='', source='', cover_path='', dynamic='', no_reprint=1, bucket=''):
        """视频投稿
        Args:
            filepath   : 视频文件路径
            title      : 投稿标题
            tid        : 投稿频道id,详见https://member.bilibili.com/x/web/archive/pre
            tag        : 视频标签，多标签使用','号分隔
            desc       : 视频描述信息
            source     : 转载视频出处url
            cover_path : 封面图片路径
            dynamic    : 分享动态, 比如："#周五##放假# 劳资明天不上班"
            no_reprint : 1表示不允许转载,0表示允许
        """
        # TODO:
        # 1.增加多P上传
        # 2.对已投稿视频进行删改, 包括删除投稿，修改信息，加P删P等

        # 上传文件, 获取上传信息
        upload_info, bucket_upload_info = self._upload_retry(filepath, bucket, source)
        # 获取图片链接
        cover_url = self._cover_up(cover_path)
        # 版权判断, 转载无版权
        copyright = 2 if source else 1
        # tag设置
        if isinstance(tag, list):
            tag = ','.join(tag)
        # 设置视频基本信息
        params = {
            'copyright' : copyright,
            'source'    : source,
            'title'     : title,
            'tid'       : tid,
            'tag'       : tag,
            'no_reprint': no_reprint,
            'desc'      : desc,
            'desc_format_id': 0,
            'dynamic': dynamic,
            'cover'     : cover_url,
            'videos'    : [{
                'filename': upload_info['bili_filename'],
                'title'   : title,
                'desc'    : '',
            }]
        }
        if bucket:
            params['videos'].append({
                'filename': bucket_upload_info['bili_filename'],
                'title': '防撞桶',
                'desc': '',
            })
        if source:
            del params['no_reprint']
        url = 'https://member.bilibili.com/x/vu/web/add?csrf=' + self.csrf
        response = self.session.post(url, json=params)
        print('SET VIDEO INFO')
        print('SET RESP', response.json())
        self.aid = json.loads(response.text)['data']['aid']
        print("AID {}".format(self.aid))

    def loadSub(self, subfile):
        subjson = {
            "fontsize": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": [{
                "from": sub.start.ordinal/1000,
                "to": sub.end.ordinal/1000,
                "location": 2,
                "content": sub.text
            } for sub in pysrt.open(subfile)]
        }
        return json.dumps(subjson, ensure_ascii=False)

    def getCid(self, aid):
        response = json.loads(requests.get(url="https://api.bilibili.com/x/player/pagelist?aid={}&jsonp=jsonp".format(aid)).text)
        while "data" not in response:
            time.sleep(600)
            response = json.loads(requests.get(url="https://api.bilibili.com/x/player/pagelist?aid={}&jsonp=jsonp".format(aid)).text)
        return response["data"][0]["cid"]

    def uploadSub(self, subfile):
        sub_url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"
        params = {
            'type': 1,
            'lan': 'zh-CN',
            'oid': self.getCid(self.aid),
            'aid': self.aid,
            'data': self.loadSub(subfile),
            'submit': True,
            'sign': True,
            'csrf': self.cookiedic["bili_jct"],
        }
        response = self.session.post(sub_url, params=params)

    def uploadDynamic(self, dynamicContent):
        dynamic_url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create"
        params = {
            'content': dynamicContent,
            'type': 4,
            'rid': 0,
            'csrf_token': self.cookiedic["bili_jct"],
        }
        response = self.session.post(dynamic_url, data=params)
        return int(json.loads(response.text)['data']['dynamic_id'])

    def getNewestDynamic(self):
        new_dy_url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid={}&type={}".format(self.uid, self.type)
        response = self.session.get(new_dy_url)
        return json.loads(response.text)["data"]["max_dynamic_id"]

    def comment(self, comment, dynamic_id):
        if not isinstance(dynamic_id, int):
            dynamic_id = self.getNewestDynamic()
        comment_url = "https://api.bilibili.com/x/v2/reply/add"
        params = {
            'oid': dynamic_id,
            'type': 17,
            'message': comment,
            'plat': 1,
            'ordering': 'heat',
            'jsonp': 'jsonp',
            'csrf': self.cookiedic["bili_jct"],
        }
        response = self.session.post(comment_url, params=params)
        print(json.loads(response.text))

if __name__=="__main__":
    uper = BilibiliUploader()
    uper.uploadDynamic("test")
    # # for i in range(20):
    # #     time.sleep(10)
    # #     uper.comment(str(i))
    # uper.upload('{}.flv'.format(435607915), '{} 2019-06-07 直播录像'.format("idke"), 136,
    #             "idke,OSU,直播,录像", "idke直播间：https://www.twitch.tv/idke", "", '{}.jpg'.format(435607915))
