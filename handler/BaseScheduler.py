import asyncio
import datetime

from config import DOWNLOAD_RETRY_DELAY, UPLOAD_RETRY_DELAY
from Downloader import Downloader, get_downloader
from Uploader import Uploader, get_uploader
from typing import Callable, Any
from BaseLoader import Task, BaseLoader
from event.Event import Event
from event.channel_events import Feed
from model import TaskPriority, TaskState

VERBOSE = True


class TaskConcurrent:
    def __init__(self, max_concurrent: int):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
        self.empty = asyncio.Event()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            await self.semaphore.acquire()
            self.max_concurrent -= 1
            if self.max_concurrent == 0:
                self.empty.set()
            else:
                self.empty.clear()

    def release(self):
        async def _release():
            async with self.lock:
                self.semaphore.release()
                self.max_concurrent += 1
                self.empty.clear()

        asyncio.create_task(_release())

    async def set_max_concurrent(self, new_concurrent: int):
        if new_concurrent <= 0:
            raise ValueError("Not valid concurrent number")
        """
        Dynamically adjust the maximum number of concurrent tasks.
        Blocks until all tasks are released.
        """
        async with self.lock:
            await self.empty.wait()
            self.max_concurrent = new_concurrent
            self.semaphore = asyncio.Semaphore(self.max_concurrent)


class TaskStateMachine:
    def __init__(self, task: Task):
        self.task: Task = task

    async def load(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def start(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def pause(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def resume(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def cancel(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def suspend(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def wait(self, scheduler: "Scheduler"):
        raise NotImplemented

    async def retry(self, scheduler: "Scheduler", delay: float = 0):
        raise NotImplemented

    async def force_start(self, scheduler: "Scheduler"):
        raise NotImplemented


class Waiting(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        current_timestamp = datetime.datetime.now().timestamp()
        if self.task.wait_time < current_timestamp:
            self.task.state = TaskState.IN_QUEUE
            await scheduler.put_task_to_queue(self.task)
        else:
            self.task.state = TaskState.WAITING
            scheduler.put_task_to_wait(self.task.wait_time - self.task, current_timestamp)

    async def force_start(self, scheduler: "Scheduler"):
        self.task = scheduler.skip_wait(self.task.id)
        self.task.state = TaskState.IN_QUEUE
        await scheduler.put_task_to_queue(self.task, TaskPriority.IN_HURRY)


class InQueue(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        await scheduler.put_task_to_queue(self.task, self.task.priority)

    async def start(self, scheduler: "Scheduler"):
        self.task.state = TaskState.PROCESSING
        await scheduler.create_worker_task(self.task)

    async def cancel(self, scheduler: "Scheduler"):
        task = await scheduler.remove_task_from_queue(self.task.id)
        scheduler.destroy_task(task)

    async def force_start(self, scheduler: "Scheduler"):
        await scheduler.skip_queue(self.task.id)


class Processing(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        await scheduler.start_task(self.task)

    async def pause(self, scheduler: "Scheduler"):
        self.task.state = TaskState.PAUSE
        await scheduler.pause_worker(self.task.id)

    async def suspend(self, scheduler: "Scheduler"):
        self.task.state = TaskState.SUSPENDED
        await scheduler.suspend_worker(self.task.id)

    async def cancel(self, scheduler: "Scheduler"):
        task = await scheduler.cancel_worker(self.task.id)
        scheduler.destroy_task(task)


class Pause(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        await scheduler.start_task(self.task)
        await scheduler.pause_worker(self.task.id)

    async def resume(self, scheduler: "Scheduler"):
        self.task.state = TaskState.PROCESSING
        await scheduler.resume_worker(self.task.id)

    async def force_start(self, scheduler: "Scheduler"):
        self.task.state = TaskState.PROCESSING
        await scheduler.resume_worker(self.task.id)


class Suspended(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        scheduler.put_worker_to_suspend(scheduler.create_worker(self.task))

    async def resume(self, scheduler: "Scheduler"):
        self.task.state = TaskState.IN_QUEUE
        await scheduler.put_task_to_queue(self.task)

    async def force_start(self, scheduler: "Scheduler"):
        self.task.state = TaskState.IN_QUEUE
        await scheduler.put_task_to_queue(self.task, TaskPriority.IN_HURRY)


class Completed(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        scheduler.put_task_to_complete(self.task)

    async def retry(self, scheduler: "Scheduler", delay: float = 0):
        self.task.state = TaskState.WAITING
        await scheduler.put_task_to_queue_delay(self.task, delay)


class Failed(TaskStateMachine):
    async def load(self, scheduler: "Scheduler"):
        scheduler.put_task_to_failed(self.task)

    async def retry(self, scheduler: "Scheduler", delay: float = 0):
        self.task.state = TaskState.WAITING
        await scheduler.put_task_to_queue_delay(self.task, delay)


class Scheduler:
    machines: dict[TaskState, type[TaskStateMachine]] = {
        TaskState.WAITING: Waiting,
        TaskState.IN_QUEUE: InQueue,
        TaskState.PROCESSING: Processing,
        TaskState.PAUSE: Pause,
        TaskState.COMPLETED: Completed,
        TaskState.FAILED: Failed,
    }

    def __init__(self, name: str, task_type: type[Task], get_all_tasks_from_db: Callable[..., list[Task]],
                 add_task_to_db: Callable[[Task], Any], destroy_task: Callable[[Task], Any],
                 retry_delay: int, max_concurrent: int, worker_factory: Callable[[Task], BaseLoader],
                 suspend_event: Event, feed_event: Event, pause_event: Event,
                 continue_event: Event, cancel_event: Event, force_start_event: Event):
        # variables
        self.name: str = name
        self.Task = task_type
        self.max_concurrent: TaskConcurrent = TaskConcurrent(max_concurrent)
        self.retry_delay: int = retry_delay
        # functions
        self.get_all_tasks_from_db: Callable[..., list[Task]] = get_all_tasks_from_db
        self.add_task_to_db: Callable[[Task], Any] = add_task_to_db
        self.destroy_task: Callable[[Task], Any] = destroy_task
        self.create_worker: Callable[[Task], BaseLoader] = worker_factory

        # records
        self.task_queue: asyncio.PriorityQueue[tuple[TaskPriority, int]] = asyncio.PriorityQueue()
        self.queue: dict[int, Task] = {}
        self.waiting: dict[int, Task] = {}
        self.failed: dict[int, Task] = {}
        self.completed: dict[int, Task] = {}
        self.timer_tasks: dict[int, asyncio.Task] = {}
        self.ongoing_worker_tasks: dict[int, asyncio.Task] = {}
        self.ongoing_workers: dict[int, BaseLoader] = {}
        self.suspend_workers: dict[int, BaseLoader] = {}

        # actions
        self.bind_tasks(
            suspend_event=suspend_event,
            feed_event=feed_event,
            pause_event=pause_event,
            continue_event=continue_event,
            cancel_event=cancel_event,
            force_start_event=force_start_event
        )
        self.task_load()

    def task_load(self):
        tasks = self.get_all_tasks_from_db()
        for task in tasks:
            Scheduler.machines[task.state](task).load(self)

    def bind_tasks(self, suspend_event: Event, feed_event: Event, pause_event: Event,
                   continue_event: Event, cancel_event: Event, force_start_event: Event):
        feed_event.bind(self.on_feed)
        suspend_event.bind(self.on_suspend)
        pause_event.bind(self.on_pause)
        continue_event.bind(self.on_resume)
        cancel_event.bind(self.on_cancel)
        force_start_event.bind(self.on_force_start)

    def get_ongoing_worker_task(self, id: int):
        return self.ongoing_worker_tasks[id]

    async def put_task_to_queue(self, task: Task, priority: TaskPriority = TaskPriority.DEFAULT):
        await self.task_queue.put((priority, task.id))
        self.queue[task.id] = task

    async def get_task_from_queue(self) -> Task | None:
        task_tuple = await self.task_queue.get()
        id = task_tuple[1]
        if id not in self.queue:
            return None
        task = self.queue[id]
        del self.queue[id]
        return task

    def remove_task_from_queue(self, id: int) -> Task:
        task = self.queue[id]
        del self.queue[id]
        return task

    async def put_task_to_queue_delay(self, task: Task, delay: float):
        await asyncio.sleep(delay)
        await self.put_task_to_queue(task)

    def put_task_to_wait(self, task: Task, delay: float) -> asyncio.Task:
        timer_task = asyncio.create_task(self.put_task_to_queue_delay(task, delay))
        self.waiting[task.id] = task
        self.timer_tasks[task.id] = timer_task
        return timer_task

    def put_task_to_failed(self, task: Task):
        self.failed[task.id] = task

    def put_task_to_complete(self, task: Task):
        self.completed[task.id] = task

    def put_worker_to_suspend(self, worker: BaseLoader):
        self.suspend_workers[worker.task.id] = worker

    def remove_worker_from_suspend(self, id: int) -> BaseLoader:
        worker = self.suspend_workers[id]
        del self.suspend_workers[id]
        return worker

    async def skip_queue(self, id: int):
        task = self.remove_task_from_queue(id)
        await self.put_task_to_queue(task, TaskPriority.IN_HURRY)

    async def skip_wait(self, id: int) -> Task:
        timer_task = self.timer_tasks[id]
        timer_task.cancel()
        del self.timer_tasks[id]
        task = self.waiting[id]
        del self.waiting[id]
        return task

    def get_machine(self, task: Task) -> TaskStateMachine:
        return self.machines[task.state](task)

    def get_ongoing_worker(self, id: int) -> BaseLoader:
        return self.ongoing_workers[id]

    async def start_task(self, task: Task):
        worker = self.create_worker(task)
        if task.id in self.suspend_workers:
            worker = self.remove_worker_from_suspend(task.id)
        self.ongoing_workers[task.id] = worker
        result = await worker.start()
        self.max_concurrent.release()
        return result

    async def create_worker_task(self, task: Task):
        await self.max_concurrent.acquire()
        worker_task = asyncio.create_task(self.start_task(task))
        self.ongoing_worker_tasks[task.id] = worker_task

    def _remove_worker_records(self, id: int):
        self.max_concurrent.release()
        del self.ongoing_worker_tasks[id]
        del self.ongoing_workers[id]

    async def pause_worker(self, id: int):
        worker = self.get_ongoing_worker(id)
        await worker.pause()

    async def resume_worker(self, id: int):
        worker = self.get_ongoing_worker(id)
        await worker.resume()

    async def cancel_worker(self, id: int) -> Task:
        worker = self.get_ongoing_worker(id)
        await worker.cancel()
        self._remove_worker_records(id)
        return worker.task

    async def suspend_worker(self, id: int):
        await self.pause_worker(id)
        self.put_worker_to_suspend(self.get_ongoing_worker(id))
        self._remove_worker_records(id)

    async def add_new_task(self, url: str):
        new_task = self.Task(url=url)
        persisted_task: Task = await self.add_task_to_db(new_task)
        await self.put_task_to_queue(persisted_task)

    def get_current_tasks(self):
        return [worker.task for worker in self.ongoing_workers.values()]

    def is_ongoing(self, id: int):
        return id in self.ongoing_worker_tasks

    async def on_feed(self, feed: Feed):
        await self.add_new_task(
            url=feed.url,
        )

    async def on_set_concurrent(self, concurrent: int):
        await self.max_concurrent.set_max_concurrent(concurrent)

    async def on_pause(self, task: Task):
        machine = self.get_machine(task)
        await machine.pause(self)

    async def on_resume(self, task: Task):
        machine = self.get_machine(task)
        await machine.resume(self)

    async def on_cancel(self, task: Task):
        machine = self.get_machine(task)
        await machine.cancel(self)

    async def on_force_start(self, task: Task):
        machine = self.get_machine(task)
        await machine.force_start(self)

    async def on_suspend(self, task: Task):
        machine = self.get_machine(task)
        await machine.suspend(self)

    async def run(self):
        while True:
            task = await self.get_task_from_queue()
            if task is None:
                continue
            machine = self.get_machine(task)
            await machine.start(self)