import schedule
import time
import subprocess

# 定义任务
def afk():
    print("执行AFK.py")
    subprocess.run(["python", "AFK.py"])  # 替换为AFK.py的路径

def free_shop():
    print("执行free_shop.py")
    subprocess.run(["python", "free_shop.py"])  # 替换为free_shop.py的路径

# 注册任务到时间表
schedule.every(10).seconds.do(afk)  # 每12小时执行一次AFK.py
schedule.every(24*60*60).seconds.do(free_shop)  # 每24小时执行一次free_shop.py

# 主循环，持续运行
if __name__ == "__main__":
    print("任务调度已启动...")
    while True:
        schedule.run_pending()  # 检查是否有任务需要执行
        time.sleep(3)  # 避免CPU占用过高
