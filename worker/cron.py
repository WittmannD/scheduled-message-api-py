import asyncio
import os
from datetime import datetime


from web.api.models.BaseModel import db
from worker.VKMessage import VKMessage
from worker.common.utils import fetch_messages

QUERY_INTERVAL_S = int(os.environ.get('QUERY_INTERVAL_S', 15))
TIME_RANGE_S = int(os.environ.get('TIME_RANGE_S', 60))
MAX_TASKS = 100


async def worker(name, queue) -> None:
    while True:
        message = await queue.get()

        dispatch_time = message.model.next_check_at.replace(tzinfo=None)

        while dispatch_time > datetime.utcnow():
            await asyncio.sleep(0.01)

        await message.send()

        queue.task_done()


async def dispatcher(queue) -> None:
    while True:
        start_time = datetime.utcnow()
        messages = fetch_messages(TIME_RANGE_S)
        print(f'fetched {len(messages)} messages')

        await asyncio.gather(*[queue.put(VKMessage(message)) for message in messages])

        await queue.join()
        db.session.commit()

        delay = max(0.0, float(QUERY_INTERVAL_S) - (datetime.utcnow().timestamp() - start_time.timestamp()))

        await asyncio.sleep(delay)


async def run():
    tasks = []
    task_dispatcher = None
    queue = asyncio.Queue()

    for i in range(MAX_TASKS):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    task_dispatcher = asyncio.create_task(dispatcher(queue))
    await task_dispatcher


def start():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


if __name__ == '__main__':
    start()
