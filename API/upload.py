from event.upload_events import UploadTask


class UploadAPI:
    async def get_all_upload_tasks(self):
        pass

    async def get_upload_task(self, id: int):
        pass

    async def add_new_upload_task(self, task: UploadTask):
        pass

    async def edit_upload_task(self, id: int, task: UploadTask):
        pass

    async def pause_upload_task(self, id: int):
        pass

    async def cancel_upload_task(self, id: int):
        pass

    async def force_upload(self, id: int):
        pass


def get_upload_api() -> UploadAPI:
    return UploadAPI()
