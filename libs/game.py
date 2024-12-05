import os
import time



class Game:
    def __init__(self, image_tool, action, log, window_id):
        self.image_tool = image_tool  # 工具类实例
        self.action = action  # 操作类实例
        self.log = log
        self.window_id = window_id

    @staticmethod
    def timer(seconds, activity_name):
        print("timer")  # 提示倒计时开始
        for remaining in range(seconds, -1, -1):
            print(f"\r{activity_name} 倒计时: {remaining} 秒", end="")  # 显示倒计时在同一行
            time.sleep(1)  # 等待 1 秒
        print(f"\n")  # 换行并打印结束信息


    def enter_game(self):
        print("enter_game")
        if self.image_tool.text("与服务器的连接已丢失。", offset=(0, 165)):
            self.log.info("网络错误")
            self.timer(60, "等待重连进游戏")
        if self.image_tool.picture("disconnected", offset=(-40, 80)):
            self.log.info("断线")
            self.timer(60, "等待重连进游戏")
        if self.image_tool.picture("download"):
            self.log.info("游戏更新下载")
            self.timer(60, "等待下载")
        if self.image_tool.picture("download2"):
            self.log.info("游戏更新下载")
            self.timer(60, "等待下载")

        self.image_tool.picture("adx", click_times=3)
        for _ in range(3):
            self.image_tool.text("确认", click_times=4)



    # 将装备加入图鉴或者分解
    def book(self, equip_number):
        # 初始点击项
        x_offset = -110 + (equip_number - 1) * 55  # 根据 equip_number 动态计算 x 坐标

        clicks = [
            (x_offset, -475, f"装备物品{equip_number}"),  # 动态设置装备物品的 x 坐标
            (275, -475, "排序")
        ]
        # 先执行固定的点击项
        x, y = self.image_tool.picture("bag", click_times=0)
        if x is None:
            print("无法找到图像 'bag'")
            return False
        # 执行初始点击项
        for offset in clicks:
            x_offset, y_offset, label = offset
            target_position = (x + x_offset, y + y_offset)
            self.action.click(*target_position)
            print(f"点击 {label} : {target_position}")

        for _ in range(20):
            coordinates = [(x-30,y-368), (x-10,y-365), (x+20,y-368)]
            purple = (108, 55, 158)
            orange = (173, 87 ,62)
            grey = (87, 88, 125)
            tolerance = 25
            result1 = self.image_tool.color(coordinates, orange, tolerance)
            if result1:
                print("找到橙色")
                self.image_tool.picture("X")
                self.image_tool.picture("bag", offset=(0, -400))  # 固定位置的一件装备
                self.image_tool.picture("bag", offset=(230, -140))  # 设备材料化
                self.image_tool.picture("bag", offset=(240, -350), click_times=2)  # 确认
                time.sleep(2)

            result2 = self.image_tool.color(coordinates, purple, tolerance)
            if result2:
                print("找到紫色")
                self.image_tool.picture("X")
                self.image_tool.picture("bag", offset=(0, -400))  # 固定位置的一件装备
                self.image_tool.picture("bag", offset=(370, -140))  # 收藏快捷方式

                # 判断是否需要点击空白处或红色亮点
                if self.image_tool.picture("blank", threshold=0.95, click_times=0):  # 未找到需要加入图鉴的装备
                    self.image_tool.picture("knife", offset=(0, -120))
                    # 分解装备
                    print("分解装备")
                    if self.image_tool.picture("salvage"):
                        self.image_tool.picture("ruby", offset=(130, 930))  # 分解
                        self.image_tool.picture("ruby", offset=(120, 550), click_times=2) # 确认
                else:
                    result = self.image_tool.picture("knife")
                    if result is not None:
                        x, y = result
                        self.action.drag((x, y + 320), (x, y))  # 拖拽到下一页
                        time.sleep(1)

                        # 点击查找需未加入图鉴的装备
                        base_x = x - 150
                        base_y = y + 370
                        offset = 70  # 每次偏移的量
                        # 循环进行点击操作
                        for i in range(3):  # 偏移三次
                            self.action.click(base_x + i * offset, base_y)
                            if self.image_tool.text("收藏增益登记", offset=(20, 60)):
                                self.image_tool.text("选择")
                                self.image_tool.text("确认", click_times=2)
                        self.action.drag((80, 600), (80, 1200), duration=2, steps=5)  # 拖拽回首页
                        self.image_tool.picture("knife")
                        self.image_tool.picture("knife", offset=(0, -120))
                        print("分解装备")
                        if self.image_tool.picture("salvage"):
                            self.image_tool.picture("ruby", offset=(130, 930))  # 分解
                            self.image_tool.picture("ruby", offset=(120, 550), click_times=2)  # 确认

            result3 = self.image_tool.color(coordinates, grey, tolerance)
            if result3:
                print("找到灰色")
                break
        self.image_tool.picture("100%", threshold=0.8, click_times=3)


    # 分解装备
    def salvage_equip(self, equip_type):
        coords = {
            "common": (330, -465),  # 普通
            "rare": (330, -420),  # 稀有
            "epic": (330, -375),  # 史诗
        }

        if equip_type not in coords:
            print(f"未知的装备类型: {equip_type}")
            return False


        clicks = [
            (-100, 0),  # 人物
            (55, -80),  # 装备
            (360, -490),  # 扳手
            (330, -285),  # 自动选择
            coords[equip_type],  # 根据装备类型选择坐标
            (250, -30),  # 分解
            (250, -415),  # 确认
            (250, -415),  # 确认
            (-100, 0),  # 人物
            (-100, 0)  # 人物
        ]

        base_position = self.image_tool.picture("bag", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag'")
            return False

        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.image_tool.picture("100%", threshold=0.8, click_times=3)


    def grow(self):
        clicks = [
            (-100, 0),  # 人物
            (-80, -75),  # 成长
            (300, -680),  # 升级
            (-100, 0)  # 人物
        ]
        base_position = self.image_tool.picture("bag", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.image_tool.picture("100%", threshold=0.8, click_times=3)

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

    def in_fight(self):
        if self.image_tool.picture("auto_red", click_times=0):
            print("in_fight")
            return True
        else:
            print("not in_fight")
            return False


    def choose_map(self):
        """
        根据窗口 ID 从 .env 文件中加载地图编号并映射到图片和偏移值。
        """
        # 定义图片和关卡偏移的映射
        map_info = {
            "0": ("town", 0),
            "1": ("forest", 80),
            "2": ("carrot", 80),
            "3": ("snow", 80),
            "4": ("mush", 80),
            "5": ("blue", 80),
            "6": ("sand", 80),
            "7": ("skull", 80),
            "8": ("tree", 80),
            "9": ("fire", 80),
            "10": ("shadow", 80),
            "11": ("coral", 80),
            "12": ("wind", 80),

        }

        # 获取当前窗口 ID
        window_id = self.window_id
        print(f"当前窗口 ID: '{window_id}'")

        # 从 .env 文件中读取对应的编号配置
        map_code = os.getenv(window_id)
        if not map_code:
            print(f"未找到窗口 ID '{window_id}' 的地图编号配置，请检查 .env 文件")
            return

        # 检查 map_code 是否为两位数
        if len(map_code) != 2 or not map_code.isdigit():
            print(f"地图编号 '{map_code}' 格式错误，应为两位数字，例如 '11' 或 '42'")
            return

        # 拆分编号
        image_key = map_code[0]  # 图片编号
        level = int(map_code[1])  # 关卡编号

        # 获取图片名和基础偏移值
        map_num = map_info.get(image_key)
        if not map_num:
            print(f"未找到图片编号 '{image_key}' 的映射配置，请检查代码")
            return

        image, base_offset_x = map_num
        if level < 0 or level > 5:
            print(f"关卡编号 '{level}' 超出范围，仅支持 0-5")
            return

        # 去掉  后缀，提取纯图片名称
        image_name = os.path.splitext(image)[0]

        # 计算最终偏移值：每个关卡增加 80 的偏移
        offset_x = base_offset_x * level
        offset_y = 0  # 偏移 Y 默认固定为 0

        # 检查是否在战斗中
        if not self.in_fight():
            # 执行地图切换操作
            self.switch("auto_red")
            self.image_tool.picture("bag", offset=(100, 0))  # 点击战斗
            self.image_tool.picture("bag", offset=(30, -70))  # 点击场地
            if 4 < int(image_key) < 9:
                self.image_tool.picture("right")
                time.sleep(2)
            if 8 < int(image_key) < 13:
                self.image_tool.picture("right")
                self.action.drag((100,760), (100,100))
                time.sleep(2)
            self.image_tool.picture(image, offset=(offset_x, offset_y))
            self.action.click(20, 20)
            self.action.click(20, 20)
            # 根据 level 打印不同的日志信息
            if level == 0:  # 回城镇
                print(f"{window_id} 回城")
            else:  # 其他关卡
                print(f"{window_id} 去往地图 {image_name}, 第 {level} 关")
            self.timer(15, "等待地图加载")

    def collect_diamond(self):
        for _ in range(3):
            self.image_tool.picture("100%", threshold=0.8, click_times=2)

        # 检查拆解装备
        if self.image_tool.text("装备获取", click_times=0):
            print("拆解普通装备")
            self.salvage_equip("common")
        if self.image_tool.text("设备拆装", click_times=0):
            print("拆解所有装备")
            self.salvage_equip("common")
            self.salvage_equip("rare")
            self.action.click(46, 1022)  # 角色
            self.action.click(183, 934)  # 角色
            for i in range(1, 7):
                self.book(i)
            # 完成所有操作后点击回到主界面
            self.action.click(20, 20)
            self.action.click(20, 20)
        if self.image_tool.text("升级", click_times=0):
            print("拆解所有装备")
            self.salvage_equip("common")
            self.salvage_equip("rare")
            self.action.click(46, 1022)  # 角色
            self.action.click(183, 934)  # 角色
            for i in range(1, 7):
                self.book(i)
            # 完成所有操作后点击回到主界面
            self.action.click(20, 20)
            self.action.click(20, 20)
            self.grow()

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
        self.image_tool.picture("toyz", offset=(-200, 0))  # 背包
        self.image_tool.picture("toyz", offset=(-300, -520))  # 箱子

        for _ in range(6):
            self.image_tool.picture("toyz", offset=(-280, -430))  # 第一个物品
            if self.image_tool.text("使用物品"):
                result = self.image_tool.text("确认")
                if result is not None:
                    x, y = result
                    self.action.click(x, y)
                    time.sleep(5)
                    self.action.click(x, y), self.action.click(x, y)
            else:
                break
        self.action.click(20, 20)


    def toyz(self):
        self.log.info("放置Toyz")
        self.image_tool.picture("bag", offset=(200, 0)), time.sleep(2)
        if (self.image_tool.picture("+", click_times=1)
                or self.image_tool.text("领取慎察奖励", click_times=2)
                or self.image_tool.text("领取值察奖励", click_times=2)
                or self.image_tool.text("领取察奖励", click_times=2)):
            self.image_tool.picture("+", click_times=1)

            result = self.image_tool.text("确认", click_times=0)
            if result is not None:
                x, y = result
                self.action.click(x - 282, y - 309), self.action.click(x - 282, y - 309)  # 选取第0个
                self.action.click(x - 87, y - 628)  # 放置第0个
                self.action.click(x - 185, y - 304), self.action.click(x - 185, y - 304)  # 选取第1个
                self.action.click(x - 182, y - 627)  # 放置第1个
                self.action.click(x - 88, y - 303), self.action.click(x - 88, y - 303)  # 选取第2个
                self.action.click(x - 136, y - 706)  # 放置第2个
                self.action.click(x + 16, y - 304), self.action.click(x + 16, y - 304)  # 选取第3个
                self.action.click(x - 36, y - 702)  # 放置第3个
                self.action.click(x + 111, y - 309), self.action.click(x + 111, y - 309)  # 选取第4个
                self.action.click(x + 12, y - 627)  # 放置第4个
                self.action.click(x - 231, y - 231), self.action.click(x - 231, y - 231)  # 选取第5个
                self.action.click(x - 39, y - 552)  # 放置第5个
                self.action.click(x - 134, y - 238), self.action.click(253, 758)  # 选取第6个
                self.action.click(x - 135, y - 557)  # 放置第6个

                self.action.click(x, y)  # 确认
                self.image_tool.text("开始ToyZ慎察")
                self.image_tool.text("开始ToyZ俱察")
                self.image_tool.text("开始ToyZ察")
        self.action.click(20, 20)  # 返回主界面


    def task_24(self):
        self.log.info("领每日免费宝石")
        self.image_tool.picture("bag", offset=(400, 0))
        self.image_tool.text("套餐商店")
        self.image_tool.text("日常套餐")
        self.image_tool.text("日带套餐")
        if not self.image_tool.text("SOLDOUT"):
            if self.image_tool.text("Free"):
                self.image_tool.text("购买")
                self.image_tool.text("确认")
        self.image_tool.picture("X")


        self.log.info("罗马竞技场")
        clicks = [
            (100, 0),  # 战斗
            (200, -75),  # 地下城
            (0, -770),  # 单人地下城
        ]
        base_position = self.image_tool.picture("bag", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)

        self.image_tool.text("战斗准备")
        if not self.image_tool.text("0/1"):
            self.image_tool.text("入口")
            for _ in range(5):
                if self.image_tool.text("0/1", offset=(-170, 0)):
                    break
                else:
                    self.image_tool.text("重试")
                time.sleep(20)
        self.action.click(20, 20)
        self.action.click(20, 20)


        self.log.info("地下城")
        self.switch("auto_green")
        for i in range(5):
            self.image_tool.picture("bag", offset=(100, 0))
            self.image_tool.text("地下城")
            self.image_tool.text("单人地下城")
            if self.image_tool.text("012", region=(0, 600, 500, 300)):
                self.action.drag((300, 700), (300, 300))
                if self.image_tool.text("012", region=(0, 600, 500, 300)):
                    break
                else:
                    self.image_tool.text("入口", region=(0, 600, 580, 300))
                    time.sleep(5)
                    self.action.press("A", second=3)
                    self.action.press("S", second=3)
                    self.action.press("D", second=5)
                    self.action.press("W", second=5)
                    self.action.press("A", second=5)
                    time.sleep(10)
                    if not self.image_tool.picture("ad", offset=(-180, 0)):
                        self.image_tool.text("确认")
                    if self.image_tool.picture("exit"):
                        self.image_tool.text("出口")
        self.action.click(20, 20)
        self.action.click(20, 20)
        self.switch("auto_red")


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





