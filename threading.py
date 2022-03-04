import asyncio
import threading

import time


def hard_work():
    print('thread id:', threading.get_ident())
    time.sleep(10)


async def do_async_job():
    # 單thread
    hard_work()
    # 多thread
    await asyncio.to_thread(hard_work)
    await asyncio.sleep(1)
    print('job done!')


async def main():
    task1 = asyncio.create_task(do_async_job())
    task2 = asyncio.create_task(do_async_job())
    task3 = asyncio.create_task(do_async_job())
    start = time.time()
    await asyncio.gather(task1, task2, task3)
    print('cost: ' + str(time.time()-start))


asyncio.run(main())