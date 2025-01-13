import libs.config as config
from libs.log import Log
from libs.game import Game
from libs.new import New
from libs.tool import ImageTool, Action, Window
from libs.scheduler import Scheduler
import time

cycle_time = config.get_cycle_time()
def timer(seconds, activity_name, window_id):
    for remaining in range(seconds, -1, -1):
        print(f"\r{window_id} {activity_name}: {remaining} 秒", end="")  # 显示倒计时在同一行
        time.sleep(1)  # 等待 1 秒
    print(f"\n")  # 换行并打印结束信息


def pha(window_id):
    while True:
        try:
            window = Window(window_id)
            log = Log(window_id)
            action = Action(window)
            image_tool = ImageTool(window, action)
            game = Game(window, image_tool, action, log)
            new = New(window, image_tool, action, game, log)
            scheduler = Scheduler(window_id, window, image_tool, action, game, log)

            # 尝试进入游戏，失败则重新尝试
            if not game.enter_game():
                print(f"窗口 {window_id} 进入游戏失败，准备重新尝试。")
                time.sleep(60)
                continue  # 跳过当前循环，重新开始

            game.handle_dialog()
            game.choose_map()
            game.collect_diamond()

            # 如果是新任务，执行新手引导任务
            if config.is_new(window_id):
                new.task_guide()

            # 执行每日任务
            scheduler.pending_task(window_id)
            action.click(40, 275)  # 点击自动休眠
            game.switch_rarity(window_id)

            timer(cycle_time, "等待下一次循环", window_id)
        except Exception as e:
            print("发生异常")
            time.sleep(cycle_time)
            continue


# 用于存储窗口对应的进程
window_processes = {}

if __name__ == "__main__":
    # 启动 OCR.exe
    Window.launch_ocr()

    # 获取所有账户的 window_id
    accounts = config.get_accounts()
    pha("004")
















