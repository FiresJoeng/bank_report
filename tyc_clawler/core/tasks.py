#原方案
# import asyncio
# from general_process import main_process, pb, wiseflow_logger

# import logging
# logging.basicConfig(level=logging.INFO)
# logging.info("Starting the crawling task")

# counter = 1


# async def schedule_pipeline(interval):
#     global counter
#     while True:
#         wiseflow_logger.info(f'task execute loop {counter}')
#         sites = pb.read('sites', filter='activated=True')
#         todo_urls = set()
#         for site in sites:
#             if not site['per_hours'] or not site['url']:
#                 continue
#             if counter % site['per_hours'] == 0:
#                 wiseflow_logger.info(f"applying {site['url']}")
#                 todo_urls.add(site['url'])

#         counter += 1
#         await main_process(todo_urls)
#         wiseflow_logger.info(f'task execute loop finished, work after {interval} seconds')
#         await asyncio.sleep(interval)


# async def main():
#     interval_hours = 1
#     interval_seconds = interval_hours * 60 * 60
#     await schedule_pipeline(interval_seconds)

# asyncio.run(main())

#获取数据新方案
import asyncio
from general_process import main_process, pb, wiseflow_logger

import logging
logging.basicConfig(level=logging.INFO)
logging.info("Starting the crawling task")

counter = 1

# 定义一个周期性执行的任务
async def schedule_pipeline(interval):
    global counter
    while True:
        wiseflow_logger.info(f'task execute loop {counter}')
        
        # 从 PocketBase 获取激活的网站信息
        sites = pb.read('sites', filter='activated=True')
        todo_urls = set()

        for site in sites:
            if not site['per_hours'] or not site['url']:
                continue
            # 判断当前循环是否符合每小时的执行频率
            if counter % site['per_hours'] == 0:
                wiseflow_logger.info(f"applying {site['url']}")
                todo_urls.add(site['url'])

        counter += 1
        
        # 调用爬虫主函数，传递待处理的 URL
        await main_process(todo_urls)
        
        wiseflow_logger.info(f'task execute loop finished, work after {interval} seconds')
        
        # 每次执行完任务后休息指定的时间间隔（秒）
        await asyncio.sleep(interval)

# 主执行函数，控制周期执行
async def main():
    interval_hours = 1  # 设置每小时执行一次
    interval_seconds = interval_hours * 60 * 60  # 转换为秒
    await schedule_pipeline(interval_seconds)

# 启动主任务
asyncio.run(main())

