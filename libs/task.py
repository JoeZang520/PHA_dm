import random
import time
import libs.config as config


class Task:
    def __init__(self, window, image_tool, action, log):
        self.image_tool = image_tool
        self.action = action
        self.window = window
        self.log = log
        self.config = config

    @staticmethod
    def timer(seconds, activity_name):
        print("timer")  # 提示倒计时开始
        for remaining in range(seconds, -1, -1):
            print(f"\r{activity_name} 倒计时: {remaining} 秒", end="")  # 显示倒计时在同一行
            time.sleep(1)  # 等待 1 秒
        print(f"\n")  # 换行并打印结束信息

    def esc(self):
        self.action.press("esc")
        time.sleep(1)
        self.action.press("esc")
        time.sleep(1)
        self.image_tool.text("消除")

    def wait_page_loaded(self, timeout=60):
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.image_tool.picture("ruby", click_times=0):
                return
            print(f"等待加载画面... ({elapsed_time}/{timeout} 秒)")
            time.sleep(1)  # 每秒检查一次
            elapsed_time += 1

    def switch(self, target_image):
        image_list = ["auto_grey", "auto_red", "auto_green"]
        # 检查目标图像是否在列表中
        if target_image not in image_list:
            print(f"错误：目标图像 {target_image} 不在有效图像列表中。")
            return False
        for _ in range(2):
            for image in image_list:
                coords = self.image_tool.picture(image, click_times=0)  # 获取图片的坐标
                if coords:  # 如果找到了当前图像
                    if image == target_image:
                        return True
                    else:
                        self.action.click(*coords)
                        break


    def collect_mail(self):
        self.image_tool.picture("mail")
        for _ in range(4):
            self.image_tool.text("收到", click_times=2)
        self.action.click(20, 20)
        self.action.click(20, 20)

    def collect_task(self):
        clicks = [
            (410, -790),  # 寻求
            (-20, -750),  # 每日任务
            (330, -140),  # 全部接收
            (330, -140),  # 全部接收
            (150, -750),  # 周常任务
            (330, -140),  # 全部接收
            (330, -140),  # 全部接收
            (320, -750),  # 重复任务
            (330, -140),  # 全部接收
            (330, -140),  # 全部接收
            (330, -140),  # 全部接收
            (330, -140),  # 全部接收
            (330, -140),  # 全部接收
            (330, -140)  # 全部接收
        ]
        base_position = self.image_tool.picture("bag", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.action.click(20, 20)
        self.action.click(20, 20)

    def collect_bag(self):
        self.image_tool.picture("ruby", offset=(-110, 960))  # 背包
        self.image_tool.picture("ruby", offset=(-160, 890))  # 其它物品
        self.image_tool.picture("ruby", offset=(-215, 450))  # 箱子

        for _ in range(6):
            self.image_tool.picture("ruby", offset=(-190, 540))  # 第一个物品
            if self.image_tool.text("使用物品"):
                result = self.image_tool.text("确认")
                if result is not None:
                    x, y = result
                    self.action.click(x, y)
                    time.sleep(5)
                    self.action.click(x, y), self.action.click(x, y), self.action.click(x, y)
            else:
                break

        self.image_tool.picture("ruby", offset=(-155, 450))  # toyz碎片

        for _ in range(3):
            if self.image_tool.picture("toyz_purple", color=False):
                self.action.click(325, 350)  # 块合成
                if self.image_tool.color([(330, 720)], (177, 230, 151), tolerance=20):
                    self.action.click(330, 720)  # 确认
                    time.sleep(5)
                    self.action.click(330, 720), self.action.click(330, 720)  # 确认
                else:
                    self.action.click(330, 800)  # 空白
                    break
            time.sleep(1)

        for _ in range(5):
            if self.image_tool.picture("toyz_green", color=False):
                self.action.click(325, 350)  # 块合成
                if self.image_tool.color([(330, 720)], (177, 230, 151), tolerance=20):
                    self.action.click(330, 720)  # 确认
                    time.sleep(5)
                    self.action.click(330, 720), self.action.click(330, 720)  # 确认
                else:
                    self.action.click(330, 800)  # 空白
                    break
            time.sleep(1)

        for _ in range(10):
            if self.image_tool.picture("toyz_white", color=False):
                self.action.click(325, 350)  # 块合成
                if self.image_tool.color([(330, 720)], (177, 230, 151), tolerance=20):
                    self.action.click(330, 720)  # 确认
                    time.sleep(5)
                    self.action.click(330, 720), self.action.click(330, 720)  # 确认
                else:
                    self.action.click(330, 800)  # 空白
                    break
            time.sleep(1)

        self.action.click(20, 20)
        self.action.click(20, 20)

    def toyz(self):
        self.log.info("放置Toyz")
        self.image_tool.picture("bag", offset=(200, 0)), time.sleep(2)
        self.image_tool.picture("bag", offset=(340, -735)), time.sleep(2)
        if (self.image_tool.picture("+", click_times=1)
                or self.image_tool.text("领取", click_times=2)):
            self.image_tool.picture("+", click_times=1)

            result = self.image_tool.picture("ruby", click_times=0)
            if result is not None:
                x, y = result
                self.action.click(x - 155, y + 655), self.action.click(x - 155, y + 653)  # 选取第0个
                self.image_tool.picture("toyz_grey")  # 放置第0个
                self.action.click(x - 155 + 100, y + 655), self.action.click(x - 155 +100, y + 655)  # 选取第1个
                self.image_tool.picture("toyz_grey")  # 放置第1个
                self.action.click(x - 155 + 200, y + 655), self.action.click(x - 155 +200, y + 655)  # 选取第2个
                self.image_tool.picture("toyz_grey")  # 放置第2个
                self.action.click(x - 155 + 300, y + 655), self.action.click(x - 155 +300, y + 655)  # 选取第3个
                self.image_tool.picture("toyz_grey")  # 放置第3个
                self.action.click(x - 155 + 400, y + 655), self.action.click(x - 155 + 400, y + 655)  # 选取第4个
                self.image_tool.picture("toyz_grey")  # 放置第4个
                self.action.click(x - 155 +50, y + 655 + 70), self.action.click(x - 155 +50, y + 655 + 70)  # 选取第5个
                self.image_tool.picture("toyz_grey")  # 放置第5个
                self.action.click(x - 155 + 150, y + 655 + 70), self.action.click(x - 155 + 150, y + 655 + 70)  # 选取第6个
                self.image_tool.picture("toyz_grey")  # 放置第6个

                self.action.click(x + 125, y + 960), time.sleep(2)  # 确认
                self.image_tool.text("开始ToyZ")


        self.action.click(20, 20)  # 返回主界面


    def free_diamond(self):
        self.log.info("领每日免费宝石")
        self.image_tool.picture("bag", offset=(400, 0))
        result = self.image_tool.text("套餐商店")
        if result is not None:
            x, y = result
            self.action.click(x - 270, y - 670)  # 日常套餐
            if not self.image_tool.text("SOLDOUT"):
                self.action.click(x - 80, y - 580)  # Free
                self.action.click(x + 30, y - 340)  # 购买
                self.action.click(x - 65, y - 435)  # 确认
        self.image_tool.picture("X")

    def rome(self):
        self.log.info("罗马竞技场")
        clicks = [
            (100, 0),  # 战斗
            (200, -75),  # 地下城
            (0, -770),  # 单人地下城
            (220, -450),  # 战斗准备
        ]
        base_position = self.image_tool.picture("bag", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)

        if self.image_tool.text("入口"):
            time.sleep(2)
            if self.image_tool.picture("ruby"):
                self.esc()
                return
            else:
                for _ in range(15):
                    if not self.image_tool.picture("ad2", click_times=0):
                        self.image_tool.text("重试")
                        time.sleep(2)
                        if self.image_tool.picture("ruby"):
                            self.image_tool.text("确认")
                            return
                        self.timer(10, "等待下一次找重试")
        self.esc()

    def move_underground(self):
        self.wait_page_loaded()
        self.action.press("A", second=2)
        self.action.press("S", second=2)
        self.action.press("D", second=4)
        self.action.press("W", second=4)
        self.action.press("A", second=4)
        time.sleep(5)

    def enter_underground(self):
        if not self.image_tool.picture("ad1", click_times=0,
                                       region=(0, 600, 500, 300)):
            self.image_tool.text("入口", region=(0, 600, 500, 300))
            self.action.click(470, 810)  # 入口
            self.move_underground()
            for _ in range(5):
                if self.image_tool.picture("ad2", offset=(-210, 0)):
                    self.image_tool.picture("exit")
                    time.sleep(2)
                    self.image_tool.text("出口")
                    self.wait_page_loaded()
                    break
                else:
                    self.image_tool.text("确认")
                    self.move_underground()



    def underground(self):
        self.log.info("地下城")
        self.switch("auto_green")
        for _ in range(2):
            self.image_tool.picture("bag", offset=(100, 0))
            self.image_tool.text("地下城")
            self.image_tool.text("单人地下城")
            if self.image_tool.text("012", region=(0, 600, 500, 300)) \
                    or self.image_tool.text("0/2", region=(0, 600, 500, 300)):
                self.action.drag((300, 700), (300, 300))
                if self.image_tool.text("012", region=(0, 600, 500, 300)) \
                        or self.image_tool.text("0/2", region=(0, 600, 500, 300)):
                    self.action.click(20, 20)
                    self.switch("auto_red")
                    return
                else:
                    self.enter_underground()
            else:
                self.enter_underground()
        self.switch("auto_red")


    def collect_afk(self):
        self.log.info("领AFK奖励")
        clicks = [
            (400, -640),  # 左箭头
            (260, -770),  # AFK
            (50, -290),  # 获得奖励
            (50, -290),  # 获得奖励
        ]
        base_position = self.image_tool.picture("bag", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.action.click(20, 20)
        self.action.click(20, 20)
        self.image_tool.picture("bag", offset=(400, -640))


    def task_24(self):
        self.free_diamond()
        self.rome()
        self.underground()


    def task_12(self):
        self.log.info("领取任务奖励")
        self.collect_task()

        self.log.info("领取邮件")
        self.collect_mail()

        self.log.info("领取背包物品")
        self.collect_bag()

        # self.log.info("打团队副本")
        # clicks = [
        #     (100, 0),  # 战斗
        #     (360, -80),  # 团队副本
        #     (340, -500),  # 入口
        #     (100, 0)  # 战斗
        # ]
        # base_position = self.image_tool.picture("bag", click_times=0)
        # if base_position is None:
        #     print("无法找到图像 'bag'")
        #     return False
        # for offset in clicks:
        #     target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
        #     self.action.click(*target_position)

    def task_5(self):
        self.collect_afk()

    def task_2(self):
        self.toyz()

    def perform(self, task_name):
        """通用执行任务方法"""
        if hasattr(self, task_name):
            method = getattr(self, task_name)
            method()
        else:
            print(f"Task method {task_name} does not exist.")








