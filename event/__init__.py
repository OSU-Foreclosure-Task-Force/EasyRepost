# Declaration of global events.
# If you need to build your own events,
# import Event base class and rewrite the emit() function to specify the payload type.

from .Events import FeedEvent

feed_broadcast = FeedEvent("Incoming feed")

from .Events import DownloadEvent

new_download = DownloadEvent("New download task")
new_download_created = DownloadEvent("New download task created")
edit_download = DownloadEvent("Edit download task")
download_edited = DownloadEvent("Download task edited successfully")
downloading = DownloadEvent("Task start Downloading")
download_pause = DownloadEvent("Download task pause")
download_resume = DownloadEvent("Download task resume")
download_cancel = DownloadEvent("Download task cancel")
download_suspend = DownloadEvent("Download task suspended")
force_download = DownloadEvent("Forcing a task to download")
download_complete = DownloadEvent("Download task completed")
download_retry = DownloadEvent("Download task retrying")
download_waiting = DownloadEvent("Download task waiting")

from .Events import MessageEvent

download_notification = MessageEvent("Download notification")
upload_notification = MessageEvent("Upload notification")

send_mail = MessageEvent("Send a mail")
send_short_msg = MessageEvent("Send a short message")
send_discord = MessageEvent("Send a discord message")
send_qq = MessageEvent("Send a qq message")

from .Events import ValidationEvent

validation = ValidationEvent("Incoming validation")

from .Events import HubEvent

from .Events import SubscriptionEvent

subscribe = SubscriptionEvent("Subscribing a topic")
subscribe_complete = SubscriptionEvent("Topic successfully subscribed")
unsubscribe = SubscriptionEvent("Unsubscribing a topic")
unsubscribe_complete = SubscriptionEvent("Topic successfully unsubscribed")

from .Events import UploadEvent

new_upload = UploadEvent("New upload task")
new_upload_created = UploadEvent("New upload task created")
edit_upload = UploadEvent("Edit upload task")
upload_edited = UploadEvent("Upload task edited successfully")
uploading = UploadEvent("Task start Uploading")
upload_pause = UploadEvent("Upload task pause")
upload_resume = UploadEvent("Upload task resume")
upload_cancel = UploadEvent("Upload task cancel")
upload_suspend = UploadEvent("Upload task suspended")
force_upload = UploadEvent("Forcing a task to upload")
upload_complete = UploadEvent("Upload task completed")
upload_retry = UploadEvent("Upload task retrying")
upload_waiting = UploadEvent("Upload task waiting")

from .Events import ExceptionEvent

download_error = ExceptionEvent("Download process encountered an error")
map(download_error.listen_error_on, DownloadEvent.get_all_instances())

upload_error = ExceptionEvent("Upload process encountered an error")
map(upload_error.listen_error_on, UploadEvent.get_all_instances())

subscription_error = ExceptionEvent("Subscription process encountered an error")
map(subscription_error.listen_error_on, SubscriptionEvent.get_all_instances())

all_event_error = ExceptionEvent("some process encountered an error")
map(all_event_error.listen_on, ExceptionEvent.get_all_instances())
