import time
import json
from datetime import datetime, timedelta
from libs.log import Log
from libs.game import Game
from libs.tool import ImageTool, Action, Window
from dotenv import load_dotenv
import os
import multiprocessing

# 加载 .env 文件
load_dotenv()

# 定义任务状态文件路径
PENDING_FILE = os.path.join("logs", "pending.json")

class Scheduler:
    def __init__(self, cycle_time):
        self.cycle_time = cycle_time
        self.pending = self.load_pending(PENDING_FILE)
        self.tasks = {
            "task_24": 24 * 60 * 60,
            "task_12": 12 * 60 * 60,
            "task_5": 5 * 60 * 60,
        }

    def load_pending(self, file_path):
        """从文件加载 pending 状态"""
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    def save_pending(self, file_path, state):
        """保存 pending 状态到文件"""
        with open(file_path, "w") as f:
            json.dump(state, f, indent=4)

    def process_window(self, window_id, tasks):
        log = Log(window_id)
        window = Window(window_id)
        action = Action(window)
        image_tool = ImageTool(action)
        game = Game(image_tool, action, log, window_id)

        # 打开窗口
        window.open_window()

        # 只有在检测到维护画面时才关闭窗口
        if image_tool.image("maintain.png", click_times=0):
            log.info("游戏维护")
            window.close_window()
            action.click(400, 695)  # 点击关闭按钮
            return  # 结束该窗口的处理，跳过后续操作

        # 进入游戏并执行日常操作
        game.enter_game()
        game.choose_map()
        action.press("S", 0.5)  # 随便位移一下，防止掉线了但画面依然静止不动

        # 检查领取钻石
        game.collect_diamond()

        # 检查toyz侦察
        action.click(354, 1016), time.sleep(2)
        if (image_tool.image("+.png", click_times=0) or
                image_tool.image("ling.png", click_times=0)):
            game.toyz()
        else:
            action.click(354, 1016)

        # 动态检查任务是否需要执行
        now = datetime.now()
        for task_name, interval_seconds in tasks.items():
            last_execution = self.pending[window_id].get(task_name)
            if last_execution is None or now - datetime.fromisoformat(last_execution) >= timedelta(
                    seconds=interval_seconds):
                log.info(f"执行任务 {task_name}")
                # 调用对应的任务
                task_method = getattr(game, task_name, None)
                if callable(task_method):
                    task_method()
                    self.pending[window_id][task_name] = datetime.now().replace(microsecond=0).isoformat()
                    self.save_pending(PENDING_FILE, self.pending)  # 保存状态到文件
                else:
                    log.error(f"任务 {task_name} 未定义！")

    def run(self, window_ids):
        # 初始化每个窗口的任务上次执行时间
        for window_id in window_ids:
            if window_id not in self.pending:
                self.pending[window_id] = {task: None for task in self.tasks}

        while True:
            # 使用多进程并行处理每个窗口
            processes = []
            for window_id in window_ids:
                p = multiprocessing.Process(target=self.process_window, args=(window_id, self.tasks))
                processes.append(p)
                p.start()

            # 等待所有进程完成
            for p in processes:
                p.join()

            # 每次循环结束后，等待指定时间（如120秒）
            Game.timer(self.cycle_time, "等待下一次循环")
