import libs.config as config
from libs.log import Log
from libs.game import Game
from libs.new import New
from libs.tool import ImageTool, Action, Window
from libs.scheduler import Scheduler
import multiprocessing

def pha(window_id):
    window = Window(window_id)
    log = Log(window_id)
    action = Action(window)
    image_tool = ImageTool(window, action)
    game = Game(window, image_tool, action, log)
    new = New(window, image_tool, action, game, log)
    scheduler = Scheduler(window_id,  window, image_tool, action, log)
    cycle_time = config.get_cycle_time()

    while True:
        game.enter_game()
        game.handle_dialog()
        if config.is_new(window_id):
            new.task_guide()
        if game.in_afk():
            image_tool.text("退出睡眠")
            game.collect_diamond()
            scheduler.pending_task()
            image_tool.text("自动休眠")
            game.switch_rarity(window_id)
        else:
            game.choose_map()
            game.collect_diamond()
            scheduler.pending_task()
            image_tool.text("自动休眠")
            game.switch_rarity(window_id)

        game.timer(cycle_time, "等待下一次循环")  # 5 分钟，单位：秒

if __name__ == "__main__":
    # 获取所有账户的 window_id
    accounts = config.get_accounts()

    # 创建一个进程池来并行处理多个窗口
    with multiprocessing.Pool(processes=len(accounts)) as pool:
        pool.map(pha, accounts.keys())  # 遍历所有账户并执行任务
