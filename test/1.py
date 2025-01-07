import libs.config as config
from libs.log import Log
from libs.game import Game
from libs.new import New
from libs.tool import ImageTool, Action, Window
from libs.scheduler import Scheduler
import multiprocessing
import time


def timer(seconds, window_id):
    for remaining in range(seconds, -1, -1):
        print(f"\r{window_id} 倒计时: {remaining} 秒", end="")  # 显示倒计时在同一行
        time.sleep(1)  # 等待 1 秒
    print(f"\n")  # 换行并打印结束信息

def pha(window_id):
    window = Window(window_id)
    log = Log(window_id)
    action = Action(window)
    image_tool = ImageTool(window, action)
    game = Game(window, image_tool, action, log)
    new = New(window, image_tool, action, game, log)
    scheduler = Scheduler(window_id, window, image_tool, action, game, log)

    if not game.enter_game():
        return
    game.handle_dialog()
    game.choose_map()

    # 如果是新任务，执行新手引导任务
    if config.is_new(window_id):
        new.task_guide()

    # 如果进入了 AFK 状态，执行退出 AFK 操作
    elif game.in_afk():
        image_tool.text("退出睡眠")
        game.collect_diamond()

    # 执行每日任务
    scheduler.pending_task(window_id)
    action.click(40, 275)  # 点击自动休眠
    game.switch_rarity(window_id)


if __name__ == "__main__":
    # 获取所有账户的 window_id
    accounts = config.get_accounts()
    cycle_time = config.get_cycle_time()

    pha("006")








