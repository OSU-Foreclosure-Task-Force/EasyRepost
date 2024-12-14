import asyncio
import datetime
from typing import Callable, Any, Coroutine
from BaseLoader import BaseLoader
from event.Event import Event
from event.channel_events import Feed
from model import TaskPriority, TaskState, Task

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
        self._task: Task = task

    async def load(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def start(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def pause(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def resume(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def cancel(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def suspend(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def wait(self, scheduler: "BaseScheduler"):
        raise NotImplemented

    async def retry(self, scheduler: "BaseScheduler", delay: float = 0):
        raise NotImplemented

    async def force_start(self, scheduler: "BaseScheduler"):
        raise NotImplemented


class Waiting(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        current_timestamp = datetime.datetime.now().timestamp()
        if self._task.wait_time < current_timestamp:
            self._task = await scheduler.update_task_state(self._task, TaskState.IN_QUEUE)
            await scheduler.put_task_to_queue(self._task)
        else:
            self._task = await scheduler.update_task_state(self._task, TaskState.WAITING)
            await scheduler.put_task_to_wait(self._task,self._task.wait_time - current_timestamp)

    async def force_start(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.skip_wait(self._task.id)
        self._task = await scheduler.update_task_state(self._task, TaskState.IN_QUEUE)
        await scheduler.put_task_to_queue(self._task, TaskPriority.IN_HURRY)


class InQueue(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        await scheduler.put_task_to_queue(self._task, self._task.priority)

    async def start(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.PROCESSING)
        await scheduler.create_worker_task(self._task)

    async def cancel(self, scheduler: "BaseScheduler"):
        task = await scheduler.remove_task_from_queue(self._task.id)
        scheduler.destroy_task(task)

    async def force_start(self, scheduler: "BaseScheduler"):
        await scheduler.skip_queue(self._task.id)


class Processing(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        await scheduler.start_task(self._task)

    async def pause(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.PAUSE)
        await scheduler.pause_worker(self._task.id)

    async def suspend(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.SUSPENDED)
        await scheduler.suspend_worker(self._task.id)

    async def cancel(self, scheduler: "BaseScheduler"):
        task = await scheduler.cancel_worker(self._task.id)
        scheduler.destroy_task(task)


class Pause(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        await scheduler.start_task(self._task)
        await scheduler.pause_worker(self._task.id)

    async def resume(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.PROCESSING)
        await scheduler.resume_worker(self._task.id)

    async def force_start(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.PROCESSING)
        await scheduler.resume_worker(self._task.id)


class Suspended(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        scheduler.put_worker_to_suspend(scheduler.create_worker(self._task))

    async def resume(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.IN_QUEUE)
        await scheduler.put_task_to_queue(self._task)

    async def force_start(self, scheduler: "BaseScheduler"):
        self._task = await scheduler.update_task_state(self._task, TaskState.IN_QUEUE)
        await scheduler.put_task_to_queue(self._task, TaskPriority.IN_HURRY)


class Completed(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        scheduler.put_task_to_complete(self._task)

    async def retry(self, scheduler: "BaseScheduler", delay: float = 0):
        self._task = await scheduler.update_task_state(self._task, TaskState.WAITING)
        await scheduler.put_task_to_queue_delay(self._task, delay)


class Failed(TaskStateMachine):
    async def load(self, scheduler: "BaseScheduler"):
        scheduler.put_task_to_failed(self._task)

    async def retry(self, scheduler: "BaseScheduler", delay: float = 0):
        self._task = await scheduler.update_task_state(self._task, TaskState.WAITING)
        await scheduler.put_task_to_queue_delay(self._task, delay)


class BaseScheduler:
    machines: dict[TaskState, type[TaskStateMachine]] = {
        TaskState.WAITING: Waiting,
        TaskState.IN_QUEUE: InQueue,
        TaskState.PROCESSING: Processing,
        TaskState.PAUSE: Pause,
        TaskState.COMPLETED: Completed,
        TaskState.FAILED: Failed,
    }

    FAKE_EVENT = Event("fake")

    def __init__(self, name: str,
                 task_type: type[Task],
                 get_all_tasks_from_db: Callable[..., Coroutine[Any, Any, list[Task]]],
                 add_task_to_db: Callable[[Task], Coroutine[Any, Any, Any]],
                 update_db_task: Callable[[Task], Coroutine[Any, Any, Any]],
                 destroy_task: Callable[[Task], Coroutine[Any, Any, Any]],
                 retry_delay: float,
                 max_concurrent: int,
                 worker_factory: Callable[[Task], BaseLoader],
                 suspend_event: Event = None,
                 feed_event: Event = None,
                 pause_event: Event = None,
                 resume_event: Event = None,
                 cancel_event: Event = None,
                 force_start_event: Event = None,
                 retry_event: Event = None,
                 new_task_event: Event = None,
                 wait_event: Event = None,
                 processing_event: Event = None,
                 complete_event: Event = None):
        # variables
        self._name: str = name
        self._Task = task_type
        self._max_concurrent: TaskConcurrent = TaskConcurrent(max_concurrent)
        self._retry_delay: float = retry_delay * 60
        self._retry_event: Event = retry_event if retry_event else self.FAKE_EVENT
        self._new_task_event: Event = new_task_event if new_task_event else self.FAKE_EVENT
        self._processing_event: Event = processing_event if processing_event else self.FAKE_EVENT
        self._complete_event: Event = complete_event if complete_event else self.FAKE_EVENT
        self._wait_event: Event = wait_event if wait_event else self.FAKE_EVENT

        # functions
        self.get_all_tasks_from_db: Callable[..., Coroutine[Any, Any, list[Task]]] = get_all_tasks_from_db
        self.add_task_to_db: Callable[[Task], Coroutine[Any, Any, Any]] = add_task_to_db
        self.update_db_task: Callable[[Task], Coroutine[Any, Any, Any]] = update_db_task
        self.destroy_task: Callable[[Task], Coroutine[Any, Any, Any]] = destroy_task
        self.create_worker: Callable[[Task], BaseLoader] = worker_factory

        # records
        self._task_queue: asyncio.PriorityQueue[tuple[TaskPriority, int]] = asyncio.PriorityQueue()
        self._queue: dict[int, Task] = {}
        self._waiting: dict[int, Task] = {}
        self._failed: dict[int, Task] = {}
        self._completed: dict[int, Task] = {}
        self._timer_tasks: dict[int, asyncio.Task] = {}
        self._ongoing_worker_tasks: dict[int, asyncio.Task] = {}
        self._ongoing_workers: dict[int, BaseLoader] = {}
        self._suspend_workers: dict[int, BaseLoader] = {}

        # actions
        self.bind_events(
            suspend_event=suspend_event if suspend_event else self.FAKE_EVENT,
            feed_event=feed_event if feed_event else self.FAKE_EVENT,
            pause_event=pause_event if pause_event else self.FAKE_EVENT,
            resume_event=resume_event if resume_event else self.FAKE_EVENT,
            cancel_event=cancel_event if cancel_event else self.FAKE_EVENT,
            force_start_event=force_start_event if force_start_event else self.FAKE_EVENT,
            retry_event=retry_event if retry_event else self.FAKE_EVENT,
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.task_load())

    async def task_load(self):
        tasks = await self.get_all_tasks_from_db()
        for task in tasks:
            await self.get_machine(task).load(self)

    def bind_events(self, suspend_event: Event, feed_event: Event, pause_event: Event,
                    resume_event: Event, cancel_event: Event, force_start_event: Event,
                    retry_event: Event):
        feed_event.bind(self.on_feed)
        suspend_event.bind(self.on_suspend)
        pause_event.bind(self.on_pause)
        resume_event.bind(self.on_resume)
        cancel_event.bind(self.on_cancel)
        force_start_event.bind(self.on_force_start)
        retry_event.bind(self.on_retry)

    async def update_task_state(self,task: Task,state: TaskState):
        task.state = state
        return await self.update_db_task(task)

    def get_ongoing_worker_task(self, id: int):
        return self._ongoing_worker_tasks[id]

    async def put_task_to_queue(self, task: Task, priority: TaskPriority = TaskPriority.DEFAULT):
        task.priority = priority
        task = await self.update_db_task(task)
        await self._task_queue.put((priority, task.id))
        self._queue[task.id] = task

    async def get_task_from_queue(self) -> Task | None:
        task_tuple = await self._task_queue.get()
        id = task_tuple[1]
        if id not in self._queue:
            return None
        task = self._queue[id]
        del self._queue[id]
        return task

    def remove_task_from_queue(self, id: int) -> Task:
        task = self._queue[id]
        del self._queue[id]
        return task

    async def put_task_to_queue_delay(self, task: Task, delay: float):
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass
        finally:
            await self.put_task_to_queue(task)

    async def put_task_to_wait(self, task: Task, delay: float) -> asyncio.Task:
        task.wait_time = datetime.datetime.now().timestamp() + delay
        task = await self.update_db_task(task)
        timer_task = asyncio.create_task(self.put_task_to_queue_delay(task, delay))
        self._wait_event.emit(task)
        self._waiting[task.id] = task
        self._timer_tasks[task.id] = timer_task
        return timer_task

    def put_task_to_failed(self, task: Task):
        self._failed[task.id] = task

    def put_task_to_complete(self, task: Task):
        self._completed[task.id] = task

    def put_worker_to_suspend(self, worker: BaseLoader):
        self._suspend_workers[worker.task.id] = worker

    def remove_worker_from_suspend(self, id: int) -> BaseLoader:
        worker = self._suspend_workers[id]
        del self._suspend_workers[id]
        return worker

    async def skip_queue(self, id: int):
        task = self.remove_task_from_queue(id)
        await self.put_task_to_queue(task, TaskPriority.IN_HURRY)

    async def skip_wait(self, id: int) -> Task:
        timer_task = self._timer_tasks[id]
        timer_task.cancel()
        del self._timer_tasks[id]
        task = self._waiting[id]
        del self._waiting[id]
        return task

    def get_machine(self, task: Task) -> TaskStateMachine:
        return self.machines[task.state](task)

    def get_ongoing_worker(self, id: int) -> BaseLoader:
        return self._ongoing_workers[id]

    async def create_worker_task(self, task: Task):
        await self._max_concurrent.acquire()
        worker_task = asyncio.create_task(self.start_task(task))
        self._ongoing_worker_tasks[task.id] = worker_task

    def _remove_worker_records(self, id: int):
        self._max_concurrent.release()
        del self._ongoing_worker_tasks[id]
        del self._ongoing_workers[id]

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

    def get_current_tasks(self):
        return [worker.task for worker in self._ongoing_workers.values()]

    def is_ongoing(self, id: int):
        return id in self._ongoing_worker_tasks

    async def on_feed(self, feed: Feed):
        await self.add_new_task(
            url=feed.url,
        )

    async def on_set_concurrent(self, concurrent: int):
        await self._max_concurrent.set_max_concurrent(concurrent)

    async def on_set_retry_delay(self, delay: float):
        self._retry_delay = delay * 60

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

    async def on_retry(self, task: Task):
        machine = self.get_machine(task)
        await machine.retry(task, delay=self._retry_delay)

    async def start_task(self, task: Task):
        worker = self.create_worker(task)
        if task.id in self._suspend_workers:
            worker = self.remove_worker_from_suspend(task.id)
        self._ongoing_workers[task.id] = worker
        self._processing_event.emit(task)
        result = None
        try:
            result = await worker.start()
            task = await self.update_task_state(task, TaskState.COMPLETED)
            self._complete_event.emit(task)
        except Exception as e:
            task = await self.update_task_state(task, TaskState.FAILED)
            self._processing_event.emit_exception(e, task)

        finally:
            self._max_concurrent.release()
            return result

    async def add_new_task(self, url: str):
        new_task = self._Task(url=url)
        persisted_task: Task = await self.add_task_to_db(new_task)
        await self.put_task_to_queue(persisted_task)
        self._new_task_event.emit(persisted_task)

    async def run(self):
        while True:
            task = await self.get_task_from_queue()
            if task is None:
                continue
            machine = self.get_machine(task)
            await machine.start(self)
