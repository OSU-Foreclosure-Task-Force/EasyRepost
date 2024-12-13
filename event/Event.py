from typing import Callable, Any, Coroutine
from copy import deepcopy
from pyee.asyncio import AsyncIOEventEmitter
from asyncio import iscoroutinefunction


class Event:
    """
    An Emitter that sends events in a concurrent way (using ensure_future).
    Only supports async functions, but you can pass in a wrapper to wrap sync functions into coroutines.
    If "new_listener" or "error" is passed as an event_name, it will be set to "default".
    """

    def __init__(self, event_name: str):
        """
        Initializes the event emitter with a given event name.

        :param event_name: The name of the event to bind or emit.
                            Defaults to 'default' if "new_listener" or "error" is used.
        """
        self.EVENT_NAME: str = event_name if event_name not in ("new_listener", "error") else "default"
        self._event_emitter = AsyncIOEventEmitter()

    def emit(self, payload: Any) -> bool:
        """
        Emits an event with the given payload, using deepcopy to avoid mutating the original payload.

        :param payload: The data to emit with the event.
        :return: True if the event was emitted successfully, otherwise False.
        """
        return self._event_emitter.emit(self.EVENT_NAME, deepcopy(payload))

    def emit_exception(self, exception: Exception, payload: Any) -> bool:
        """
        Emits an error event with the given payload, using deepcopy to avoid mutating the original payload.
        :param exception: The exception to emit with the event.
        :param payload: The data to emit with the event.
        :return: True if the event was emitted successfully, otherwise False.
        """
        return self._event_emitter.emit("error",exception, deepcopy(payload))

    @staticmethod
    def _wrap(callback: Callable[..., Coroutine[Any, Any, Any]],
              async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None) -> Any:
        """
        Wraps a synchronous function into a coroutine if needed.

        :param callback: The callback function to wrap.
        :param async_wrapper: An optional wrapper function that converts a sync function into a coroutine.
        :return: The callback function, wrapped as a coroutine if necessary.
        """
        if async_wrapper is not None and iscoroutinefunction(callback):
            return async_wrapper(callback)
        return callback

    def bind(self, callback: Callable[[...], Coroutine[Any, Any, Any]],
             async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None) -> Callable[
        ..., Coroutine[Any, Any, Any]]:
        """
        Binds a callback function to the event, ensuring it is wrapped correctly if needed.

        :param callback: The async function to bind to the event.
        :param async_wrapper: An optional wrapper function to convert a sync function to a coroutine.
        :return: The bound callback function.
        """
        return self._event_emitter.add_listener(self.EVENT_NAME, self._wrap(callback, async_wrapper))

    def unbind(self, callback: Callable[[...], Coroutine[Any, Any, Any]],
               async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None):
        """
        Unbinds a callback function from the event.

        :param callback: The async function to unbind from the event.
        :param async_wrapper: An optional wrapper function that converts a sync function to a coroutine.
        """
        self._event_emitter.remove_listener(self.EVENT_NAME, self._wrap(callback, async_wrapper))

    def bind_once(self, callback: Callable[[...], Coroutine[Any, Any, Any]],
                  async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None) -> \
    Callable[..., Coroutine[Any, Any, Any]]:
        """
        Binds a callback function to the event to be called only once.

        :param callback: The async function to bind to the event.
        :param async_wrapper: An optional wrapper function to convert a sync function to a coroutine.
        :return: The bound callback function, which will be called only once.
        """
        return self._event_emitter.once(self.EVENT_NAME, self._wrap(callback, async_wrapper))

    def bind_on_new_listener(self, callback: Callable[[...], Coroutine[Any, Any, Any]],
                             async_wrapper: Callable[
                                 [Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None) -> Callable[
        ..., Coroutine[Any, Any, Any]]:
        """
        Binds a callback function to the "new_listener" event.

        :param callback: The async function to bind to the "new_listener" event.
        :param async_wrapper: An optional wrapper function to convert a sync function to a coroutine.
        :return: The bound callback function for the "new_listener" event.
        """
        return self._event_emitter.add_listener("new_listener", self._wrap(callback, async_wrapper))

    def bind_on_error(self, callback: Callable[[...], Coroutine[Any, Any, Any]],
                      async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None) -> \
    Callable[..., Coroutine[Any, Any, Any]]:
        """
        Binds a callback function to the "error" event.

        :param callback: The async function to bind to the "error" event.
        :param async_wrapper: An optional wrapper function to convert a sync function to a coroutine.
        :return: The bound callback function for the "error" event.
        """
        return self._event_emitter.add_listener("error", self._wrap(callback, async_wrapper))

    def connect(self,
                async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None):
        """
        A decorator that connects the decorated function with the event.
        The function must be async and return a coroutine.

        :param async_wrapper: A wrapper that wraps a sync function into a coroutine.
                              This can be useful if you want to connect a sync function with the event.

        Usage:

        @event.connect()
        async def async_function(payload):
            pass

        or

        @event.connect(wrapper)
        def sync_function(payload):
            pass
        """

        def decorator(func: Callable[..., Any]):
            return self.bind(func, async_wrapper=async_wrapper)

        return decorator

    def connect_once(self,
                     async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None):
        """
        A decorator that connects the decorated function to be called once when the event is emitted.

        :param async_wrapper: A wrapper that wraps a sync function into a coroutine.
                              This can be useful if you want to connect a sync function with the event.

        Usage:

        @event.connect_once()
        async def async_function(payload):
            pass

        or

        @event.connect_once(wrapper)
        def sync_function(payload):
            pass
        """

        def decorator(func: Callable[..., Any]):
            return self.bind_once(func, async_wrapper=async_wrapper)

        return decorator

    def connect_on_new_listener(self,
                                async_wrapper: Callable[
                                    [Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None):
        """
        A decorator that connects the decorated function to be called when a new listener is added.

        :param async_wrapper: A wrapper that wraps a sync function into a coroutine.
                              This can be useful if you want to connect a sync function with the event.

        Usage:

        @event.connect_on_new_listener()
        async def async_function(payload):
            pass

        or

        @event.connect_on_new_listener(wrapper)
        def sync_function(payload):
            pass
        """

        def decorator(func: Callable[..., Any]):
            return self.bind_on_new_listener(func, async_wrapper=async_wrapper)

        return decorator

    def connect_on_error(self,
                         async_wrapper: Callable[[Callable[..., Any]], Callable[..., Coroutine[Any, Any, Any]]] = None):
        """
        A decorator that connects the decorated function to be called when an error occurs.

        :param async_wrapper: A wrapper that wraps a sync function into a coroutine.
                              This can be useful if you want to connect a sync function with the event.

        Usage:

        @event.connect_on_error()
        async def async_function(payload):
            pass

        or

        @event.connect_on_error(wrapper)
        def sync_function(payload):
            pass
        """

        def decorator(func: Callable[..., Any]):
            return self.bind_on_error(func, async_wrapper=async_wrapper)

        return decorator
