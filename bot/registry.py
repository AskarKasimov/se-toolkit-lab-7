from typing import Any, Callable, Coroutine

COMMAND_HANDLERS: dict[
    str, Callable[..., Coroutine[Any, Any, str]] | Callable[[], str]
] = {}
