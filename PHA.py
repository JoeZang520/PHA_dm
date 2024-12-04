import os
from dotenv import load_dotenv
from libs.schedule import Scheduler

# 加载 .env 文件
load_dotenv()

if __name__ == "__main__":
    # 动态获取窗口编号
    window_ids = [key for key in os.environ.keys() if key.isdigit()]
    cycle_time = int(os.getenv("CYCLE_TIME", 120))  # 每轮循环间隔时间（秒）

    # 初始化调度器
    scheduler = Scheduler(cycle_time)
    scheduler.run(window_ids)
