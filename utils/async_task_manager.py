#!/usr/bin/env python
# encoding: utf-8

import asyncio
from typing import Optional, Set, Dict
from contextlib import asynccontextmanager


class AsyncTaskManager:
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()
        self._stop_events: Dict[str, asyncio.Event] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False

    async def start(self):
        if self._running:
            return
        self._loop = asyncio.get_running_loop()
        self._running = True

    async def stop(self, wait: bool = True, timeout: Optional[float] = None):
        if not self._running:
            return

        self._running = False

        for event in self._stop_events.values():
            event.set()

        if wait:
            tasks = list(self._tasks)
            if tasks:
                await asyncio.wait(tasks, timeout=timeout)

    def create_task(self, coro, name: Optional[str] = None) -> asyncio.Task:
        if not self._running:
            raise RuntimeError("TaskManager not started. Call start() first.")

        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def get_stop_event(self, name: str) -> asyncio.Event:
        if name not in self._stop_events:
            self._stop_events[name] = asyncio.Event()
        return self._stop_events[name]

    @asynccontextmanager
    async def task_scope(self):
        await self.start()
        try:
            yield self
        finally:
            await self.stop()

    def is_running(self) -> bool:
        return self._running
