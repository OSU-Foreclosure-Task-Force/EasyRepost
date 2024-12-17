from model import Task


class BaseLoader:
    def __init__(self, task: Task):
        self.task: Task = task

    async def start(self):
        raise NotImplemented

    async def resume(self):
        raise NotImplemented

    async def pause(self):
        raise NotImplemented

    async def cancel(self):
        raise NotImplemented

    async def get_progress(self):
        raise NotImplemented
