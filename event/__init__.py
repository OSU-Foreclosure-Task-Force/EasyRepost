# Declaration of global events.
# If you need to build your own events,
# import Event base class and rewrite the emit() function to specify the payload type.

from event.channel_events import ChannelUpdate
channel_update = ChannelUpdate("A channel is being updated")

from event.download_events import DownloadEvent
new_download = DownloadEvent("New download task")
download_pause = DownloadEvent("Download task pause")
download_continue = DownloadEvent("Download task continue")
download_cancel = DownloadEvent("Download task cancel")
force_download = DownloadEvent("Forcing a task to download")
download_complete = DownloadEvent("Download task completed")
download_fail = DownloadEvent("Download task failed")
download_retry = DownloadEvent("Download task retrying")
download_waiting = DownloadEvent("Download task waiting")

from event.message_events import MessageEvent
download_worker_full = MessageEvent("Download worker is full")
upload_worker_full = MessageEvent("Upload worker is full")
send_mail = MessageEvent("Send a mail")
send_short_msg = MessageEvent("Send a short message")
send_discord = MessageEvent("Send a discord message")
send_qq = MessageEvent("Send a qq message")

from event.upload_events import UploadEvent
new_upload = UploadEvent("New upload task")
upload_pause = UploadEvent("Upload task pause")
upload_continue = UploadEvent("Upload task continue")
upload_cancel = UploadEvent("Upload task cancel")
force_upload = UploadEvent("Forcing a task to upload")
upload_complete = UploadEvent("Upload task completed")
upload_fail = UploadEvent("Upload task failed")
upload_retry = UploadEvent("Upload task retrying")
upload_waiting = UploadEvent("Upload task waiting")


