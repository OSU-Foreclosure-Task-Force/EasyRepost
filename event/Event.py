from typing import Callable, Any, Coroutine
from copy import deepcopy
from pyee.asyncio import AsyncIOEventEmitter
from asyncio import iscoroutinefunction


class Event:
    """
    An Emitter that sends event in a concurrent way (ensure_future)
    only support async functions, but you can pass in a wrapper to wrap sync functions into coroutine
    """

    def __init__(self, event_name):
        self.EVENT_NAME = event_name
        self.__event_emitter = AsyncIOEventEmitter()

    def emit(self, payload: Any) -> bool:
        return self.__event_emitter.emit(self.EVENT_NAME, payload=deepcopy(payload))

    def subscribe(self, callback: Callable[[str, ...], Coroutine[Any, Any, Any]],
                  async_wrapper: Callable[
                      [Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None) -> None:
        if async_wrapper is not None and iscoroutinefunction(callback):
            self.__event_emitter.add_listener(self.EVENT_NAME, async_wrapper(callback))
            return
        self.__event_emitter.add_listener(self.EVENT_NAME, callback)

    def connect(self,
                async_wrapper: Callable[
                      [Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None):
        """
        A decorator that connects the decorated function with the event
        Function requires to be async that returns a coroutine
        :async_wrapper
        A wrapper that wraps a sync function into a coroutine
        can be useful if you want to connect a sync function with the event
        """

        def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            self.subscribe(wrapper,async_wrapper=async_wrapper)
            return func

        return decorator
