import asyncio
import logging
import os
import sys
from datetime import datetime

from worker.VKMessage import VKMessage
from worker.common.utils import DB

QUERY_INTERVAL_S = int(os.environ.get('QUERY_INTERVAL_S', 15))
TIME_RANGE_S = int(os.environ.get('TIME_RANGE_S', 60))
MAX_TASKS = 100

logger = logging.getLogger('worker')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def worker(name, queue) -> None:
    while True:
        message = await queue.get()

        dispatch_time = message.model.time_for_dispatch.replace(tzinfo=None)

        delay = (dispatch_time - datetime.utcnow()).total_seconds()
        await asyncio.sleep(delay)

        await message.send()

        queue.task_done()


async def dispatcher(queue) -> None:
    while True:
        start_time = datetime.utcnow()
        messages = DB.fetch_messages(TIME_RANGE_S)
        logger.info(f'fetched {len(messages)} messages')

        await asyncio.gather(*[queue.put(VKMessage(message)) for message in messages])

        await queue.join()
        DB.commit()

        delay = max(0.0, float(QUERY_INTERVAL_S) - (datetime.utcnow().timestamp() - start_time.timestamp()))

        await asyncio.sleep(delay)


async def run():
    tasks = []
    task_dispatcher = None
    queue = asyncio.Queue()

    logger.info('starting task pull')
    for i in range(MAX_TASKS):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    task_dispatcher = asyncio.create_task(dispatcher(queue))
    await task_dispatcher


def start():
    logger.info('worker starting')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


if __name__ == '__main__':
    start()
