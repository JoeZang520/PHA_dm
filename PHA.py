import libs.config as config
from libs.log import Log
from libs.game import Game
from libs.new import New
from libs.tool import ImageTool, Action, Window
from libs.scheduler import Scheduler
import multiprocessing
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


window_processes = {}

if __name__ == "__main__":
    # 启动 OCR.exe
    Window.launch_ocr()

    # 获取所有账户的 window_id
    accounts = config.get_accounts()
    n = config.get_process_limit()
    processed_count = 0

    window_ids = list(accounts.keys())
    window_ids.reverse()

    while True:
        while processed_count < n:  # 控制启动的进程数
            for window_id in window_ids:
                # 如果该窗口没有进程或者进程已经结束，创建新的进程
                if window_id not in window_processes or not window_processes[window_id].is_alive():
                    p = multiprocessing.Process(target=pha, args=(window_id,))
                    window_processes[window_id] = p
                    p.start()  # 启动新的进程
                    timer(100, "等待下一个窗口启动", window_id)
                    processed_count += 1  # 每启动一个进程就增加计数

                    if processed_count >= n:  # 达到限制后停止
                        print("达到最大窗口数量")
                        break
                else:
                    print(f"窗口 {window_id} 已在运行，跳过重新创建进程。")
        time.sleep(cycle_time)


















