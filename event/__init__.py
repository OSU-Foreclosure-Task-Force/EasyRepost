from channel_events import *
from download_events import *
from message_events import *
from upload_events import *

channel_update = ChannelUpdate("Channel update")

new_download = NewDownload("New download task")
download_pause = DownloadPause("Download task pause")
download_continue = DownloadContinue("Download task continue")
download_cancel = DownloadCancel("Download task cancel")

download_worker_full = DownloadFull("Download worker is full")
upload_worker_full = UploadFull("Upload worker is full")
send_mail = SendMail("send a mail")
send_short_msg = SendShortMSG("send a short message")
send_discord = SendDiscord("send a discord message")
send_qq = SendQQ("send a qq message")

new_upload = NewUpload("New upload task")
upload_pause = UploadPause("Upload task pause")
upload_continue = UploadContinue("Upload task continue")
upload_cancel = UploadCancel("Upload task cancel")