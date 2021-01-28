import asyncio
import typing

from starlette.concurrency import run_in_threadpool


class BackgroundTask:
    def __init__(
        self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_async = asyncio.iscoroutinefunction(func)

    async def __call__(self) -> None:
        await self.get_coroutine()

    def get_coroutine(self) -> typing.Coroutine:
        if self.is_async:
            return self.func(*self.args, **self.kwargs)
        else:
            return run_in_threadpool(self.func, *self.args, **self.kwargs)


class BackgroundTasks(BackgroundTask):
    def __init__(self, tasks: typing.Sequence[BackgroundTask] = []):
        self.tasks = list(tasks)

    def add_task(
        self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        task = BackgroundTask(func, *args, **kwargs)
        self.tasks.append(task)

    async def __call__(self) -> None:
        await asyncio.gather(*(task.get_coroutine() for task in self.tasks))