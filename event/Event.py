from blinker import Signal
from typing import Callable, Any, Coroutine


class Event:
    def __init__(self, emit_message=""):
        self.__emit_message = emit_message
        self.__signal = Signal()

    def emit(self, any_object: Any) -> Coroutine[Any, Any, list[tuple[Callable[[...], Any], Any]]]:
        return self.__signal.send_async(self.__emit_message, payload=any_object)

    def subscribe(self, callback: Callable[[str, ...], Any]) -> None:
        self.__signal.connect(callback)

    def async_subscribe(self):
        """
        装饰器，用于将一个协程函数连接到 signal
        """

        def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
            # 包装器，将协程函数包装为一个适配的回调
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            # 连接到 signal
            self.subscribe(wrapper)
            return func

        return decorator
