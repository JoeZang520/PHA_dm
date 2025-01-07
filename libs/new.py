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
        for remaining in range(seconds, -1, -1):
            print(f"\r{activity_name} 倒计时: {remaining} 秒", end="")  # 显示倒计时在同一行
            time.sleep(1)  # 等待 1 秒
        print(f"\n")  # 换行并打印结束信息

        # 分解装备

    def salvage_equip(self, rarity):
        self.image_tool.picture("bag", offset=(-100, 0))  # 角色
        self.image_tool.picture("bag", offset=(40, -70))  # 装备
        self.image_tool.picture("bag", offset=(350, -480))  # 分解按钮
        self.image_tool.text("自动选择")
        self.image_tool.text(rarity)
        self.image_tool.text("分解")
        self.image_tool.text("确认", click_times=2)
        self.action.click(20, 20)
        self.action.click(20, 20)
        self.image_tool.picture("100%", threshold=0.8, click_times=3)

    def collect_diamond_new(self):
        for _ in range(3):
            self.image_tool.picture("100%", threshold=0.8, click_times=2)
        if self.image_tool.text("装备获取"):
            self.salvage_equip("稀有")
        if (self.image_tool.text("升级")
            or self.image_tool.text("设备拆装")):
            self.salvage_equip("稀有")
            self.image_tool.picture("bag", offset=(-100, 0))
            for i in range(1, 7):
                self.game.book(i)
            self.image_tool.text("成长")
            self.image_tool.text("升级", click_times=3)
            self.game.esc()
            self.action.click(20, 20)


    def task_guide(self):
        self.log.info("开始新手指导任务")
        self.image_tool.text("退出")
        self.collect_diamond_new()
        for _ in range(10):
            self.game.check_offline()
            for _ in range(4):
                self.image_tool.picture("bag", offset=(250, -900))  # 点击地图旁边的向右箭头，确保进入到最新的图
                self.action.click(20, 20)
                self.game.wait_page_loaded(timeout=8)
            print("点击boss")
            self.game.switch_auto("auto_green")
            self.action.click(540 , 80)  # 点击boss出现的地点
            self.action.click(300, 830)  # 点击boss出现的地点
            time.sleep(1)
            self.game.wait_page_loaded()
            if (self.image_tool.text("接受")
                    or self.game.wait_battle_start(max_wait_time=10)):
                self.game.boss()
            if self.image_tool.text("移动时"):
                break
            self.image_tool.text("指引任务", offset=(0, 90), click_times=4)
            self.image_tool.text("莉迪亚", offset=(0, 80), click_times=3)
            if not self.image_tool.picture("ad2", offset=(-80, 0)):
                self.image_tool.text("确认", click_times=2)
            self.image_tool.text("消除", offset=(175, 0))  # 点击确认 防止npc文字中包含”确认“两个字
            self.image_tool.text("审查", offset=(-175, 0))  # 点击取消
            self.image_tool.picture("left")
            self.image_tool.picture("right")
            for _ in range(4):
                self.image_tool.picture("hand", threshold=0.95, offset=(0, 40))
                time.sleep(1)
            self.image_tool.text("莉迪亚", offset=(0, 80), click_times=3)
            self.image_tool.picture("X")
            self.action.click(20, 20)
            self.action.click(20, 20)







