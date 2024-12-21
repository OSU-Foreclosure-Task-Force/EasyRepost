from models.TaskModels import Task


class BaseLoader:
    def __init__(self, task: Task):
        self.task: Task = task

    async def start(self):
        raise NotImplementedError

    async def resume(self):
        raise NotImplementedError

    async def pause(self):
        raise NotImplementedError

    async def cancel(self):
        raise NotImplementedError

    async def get_progress(self):
        raise NotImplementedError
