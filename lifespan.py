import asyncio
from contextlib import asynccontextmanager
from handler.Scheduler import get_download_scheduler,get_upload_scheduler
from model import create_tables
from fastapi import FastAPI
import config

download_scheduler_task: asyncio.Task | None = None
upload_scheduler_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # db initialize
    await create_tables()
    # scheduler initialize
    download_scheduler = get_download_scheduler()
    upload_scheduler = get_upload_scheduler()
    await download_scheduler.load_tasks()
    await upload_scheduler.load_tasks()
    task_download = asyncio.create_task(download_scheduler.run())
    task_upload = asyncio.create_task(upload_scheduler.run())
    global download_scheduler_task, upload_scheduler_task
    download_scheduler_task = task_download
    upload_scheduler_task = task_upload
    yield
    config.write_back()
