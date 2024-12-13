# Declaration of global events.
# If you need to build your own events,
# import Event base class and rewrite the emit() function to specify the payload type.

from event.channel_events import ChannelUpdate
channel_update = ChannelUpdate("A channel is being updated")

from event.download_events import DownloadEvent
new_download = DownloadEvent("New download task")
downloading = DownloadEvent("Task start Downloading")
download_pause = DownloadEvent("Download task pause")
download_resume = DownloadEvent("Download task resume")
download_cancel = DownloadEvent("Download task cancel")
download_suspend = DownloadEvent("Download task suspended")
force_download = DownloadEvent("Forcing a task to download")
download_complete = DownloadEvent("Download task completed")
download_retry = DownloadEvent("Download task retrying")
download_waiting = DownloadEvent("Download task waiting")

from event.message_events import MessageEvent
download_worker_full = MessageEvent("Download worker is full")
upload_worker_full = MessageEvent("Upload worker is full")
send_mail = MessageEvent("Send a mail")
send_short_msg = MessageEvent("Send a short message")
send_discord = MessageEvent("Send a discord message")
send_qq = MessageEvent("Send a qq message")

from event.subscription_events import SubscriptionEvent
subscribe = SubscriptionEvent("Subscribing a topic")
unsubscribe = SubscriptionEvent("Unsubscribing a topic")


from event.upload_events import UploadEvent
new_upload = UploadEvent("New upload task")
uploading = UploadEvent("Task start Uploading")
upload_pause = UploadEvent("Upload task pause")
upload_resume = UploadEvent("Upload task resume")
upload_cancel = UploadEvent("Upload task cancel")
upload_suspend = UploadEvent("Upload task suspended")
force_upload = UploadEvent("Forcing a task to upload")
upload_complete = UploadEvent("Upload task completed")
upload_retry = UploadEvent("Upload task retrying")
upload_waiting = UploadEvent("Upload task waiting")


