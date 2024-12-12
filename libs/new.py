import os
import time
import libs.config as config

class New:
    def __init__(self, window, image_tool, action, game, log):
        self.image_tool = image_tool
        self.action = action
        self.window = window
        self.game = game
        self.log = log
        self.config = config

    @staticmethod
    def timer(seconds, activity_name):
        print("timer")  # 提示倒计时开始
        for remaining in range(seconds, -1, -1):
            print(f"\r{activity_name} 倒计时: {remaining} 秒", end="")  # 显示倒计时在同一行
            time.sleep(1)  # 等待 1 秒
        print(f"\n")  # 换行并打印结束信息


    def task_guide(self):
        self.log.info("开始新手指导任务")
        self.image_tool.text("退出睡眠")
        self.game.handle_dialog()
        self.game.choose_map()
        for _ in range(10):
            for _ in range(3):
                self.image_tool.picture("bag", offset=(250, -900))  # 点击地图旁边的向右箭头，确保进入到最新的图
                self.game.wait_page_loaded()
            if (self.image_tool.text("ENTER", offset=(0, -30))
                    or self.image_tool.text("BOSS", offset=(0, 30))
                    or self.image_tool.text("8088", offset=(0, 30))):
                if (self.image_tool.text("接受")
                        or not self.image_tool.picture("ruby")):
                    time.sleep(3)
                    self.game.boss()
            if self.image_tool.text("移动时"):
                break
            self.image_tool.picture("left")
            self.image_tool.picture("right")
            self.image_tool.text("指引任务", offset=(0, 90), click_times=4)
            self.image_tool.text("莉迪亚", offset=(0, 80), click_times=3)
            if not self.image_tool.picture("ad2", offset=(-80, 0)):
                self.image_tool.text("确认", click_times=2)
            self.image_tool.text("消除", offset=(175, 0))  # 点击确认 防止npc文字中包含”确认“两个字
            self.image_tool.text("审查", offset=(-175, 0))  # 点击取消
            for _ in range(4):
                self.image_tool.picture("hand", threshold=0.95, offset=(0, 40))
            self.image_tool.picture("X")
            self.action.click(20, 20)
            self.action.click(20, 20)







