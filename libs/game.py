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
        if self.image_tool.image("100.png", threshold=0.8, offset=(-55, 75)):
            self.log.info("网络错误")
            self.timer(60, "等待重连进游戏")
        if self.image_tool.image("disconnected.png", offset=(-40, 80)):
            self.log.info("断线")
            self.timer(60, "等待重连进游戏")
        if self.image_tool.image("download.png"):
            self.log.info("游戏更新下载")
            self.timer(60, "等待下载")
        if self.image_tool.image("download2.png"):
            self.log.info("游戏更新下载")
            self.timer(60, "等待下载")

        self.image_tool.image("adx.png", click_times=3)
        self.image_tool.image("startpage1.png", offset=(0, 400), click_times=4)
        self.image_tool.image("startpage2.png", offset=(0, 590), click_times=4)


    # 将装备加入图鉴或者分解
    def book(self, equip_number):
        # 初始点击项
        x_offset = -110 + (equip_number - 1) * 55  # 根据 equip_number 动态计算 x 坐标

        base_clicks = [
            (x_offset, -490, f"装备物品{equip_number}"),  # 动态设置装备物品的 x 坐标
            (280, -490, "排序")
        ]
        # 先执行固定的点击项
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        # 执行初始点击项
        for offset in base_clicks:
            x_offset, y_offset, label = offset
            target_position = (base_position[0] + x_offset, base_position[1] + y_offset)
            self.action.click(*target_position)
            print(f"点击 {label} : {target_position}")

        for _ in range(20):
            coordinates = [(120,623), (145,624), (169,624)]
            purple = (108, 55, 158)
            orange = (173, 87 ,62)
            grey = (87, 88, 125)
            tolerance = 25
            result1 = self.image_tool.find_color(coordinates, orange, tolerance)
            if result1:
                print("找到橙色")
                self.action.click(150, 600)  # 固定位置的一件装备
                self.action.click(375,858)  # 设备材料化
                self.action.click(388,657), self.action.click(388,657)  # 确认
                time.sleep(2)

            result2 = self.image_tool.find_color(coordinates, purple, tolerance)
            if result2:
                print("找到紫色")
                self.image_tool.image("X.png")
                self.action.click(150, 600)  # 固定位置的一件装备
                self.action.click(525, 860)  # 收藏快捷方式

                # 判断是否需要点击空白处或红色亮点
                if self.image_tool.image("blank.png", threshold=0.95, click_times=0):  # 未找到需要加入图鉴的装备
                    self.action.click(300, 380)  # 点击空白处
                    # 分解装备
                    print("分解装备")
                    if self.image_tool.image("salvage.png"):  # 拆解
                        self.action.click(395, 971)  # 分解
                        self.action.click(390, 580), self.action.click(390, 580)  # 确定
                else:
                    self.action.click(520, 490)  # 点击红色亮点
                    self.action.drag((80, 890), (80, 550))  # 拖拽到下一页
                    # 点击查找需未加入图鉴的装备
                    base_x = 370
                    base_y = 865
                    offset = 70  # 每次偏移的量

                    # 循环进行点击操作
                    for i in range(3):  # 偏移三次
                        self.action.click(base_x + i * offset, base_y)
                        if self.image_tool.image("xiao.png", threshold=0.7, click_times=0):
                            self.action.click(320, 655)  # 再次选中装备
                            self.action.click(380, 890)  # 选择
                            self.action.click(380, 600), self.action.click(380, 600)  # 确认 点两次
                    self.action.drag((80, 460), (80, 1200), duration=1.0, steps=5)  # 拖拽回首页
                    self.action.click(520, 490)  # 点击红色亮点
                    self.action.click(300, 380)  # 点击空白处
                    if self.image_tool.image("salvage.png"):  # 拆解
                        self.action.click(395,971)  # 分解
                        self.action.click(390, 580), self.action.click(390, 580)  # 确定

            result3 = self.image_tool.find_color(coordinates, grey, tolerance)
            if result3:
                print("找到灰色")
                break


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

        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False

        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.image_tool.image("100%.png", threshold=0.8, click_times=3)


    def grow(self):
        clicks = [
            (-100, 0),  # 人物
            (-80, -75),  # 成长
            (300, -680),  # 升级
            (-100, 0)  # 人物
        ]
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.image_tool.image("100%.png", threshold=0.8, click_times=3)

    def switch(self, target_image):
        image_list = ["auto_grey.png", "auto_red.png", "auto_green.png"]
        # 检查目标图像是否在列表中
        if target_image not in image_list:
            print(f"错误：目标图像 {target_image} 不在有效图像列表中。")
            return False
        for _ in range(2):
            for image in image_list:
                coords = self.image_tool.image(image, click_times=0)  # 获取图片的坐标
                if coords:  # 如果找到了当前图像
                    if image == target_image:
                        return True
                    else:
                        self.action.click(*coords)
                        break

    def in_fight(self):
        if self.image_tool.image("auto_red.png", click_times=0):
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
            "0": ("town.png", 0),
            "1": ("forest.png", 80),
            "2": ("carrot.png", 80),
            "3": ("snow.png", 80),
            "4": ("mush.png", 80),
            "5": ("blue.png", 80),
            "6": ("sand.png", 80),
            "7": ("skull.png", 80),
            "8": ("tree.png", 80),
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

        # 去掉 .png 后缀，提取纯图片名称
        image_name = os.path.splitext(image)[0]

        # 计算最终偏移值：每个关卡增加 80 的偏移
        offset_x = base_offset_x * level
        offset_y = 0  # 偏移 Y 默认固定为 0

        # 检查是否在战斗中
        if not self.in_fight():
            # 执行地图切换操作
            self.switch("auto_red.png")
            self.image_tool.image("bag.png", offset=(100, 0))  # 点击战斗
            self.image_tool.image("bag.png", offset=(30, -70))  # 点击场地
            if 4 < int(image_key) < 9:
                self.image_tool.image("right.png")
                time.sleep(2)
            self.image_tool.image(image, offset=(offset_x, offset_y))
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
            self.image_tool.image("100%.png", threshold=0.8, click_times=2)

        # 检查拆解装备
        if self.image_tool.image("huo.png", click_times=0):
            print("拆解普通装备")
            self.salvage_equip("common")
        if self.image_tool.image("chai.png", click_times=0):
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
        if self.image_tool.image("sheng.png", click_times=0):
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
        self.image_tool.image("mail.png")
        for _ in range(4):
            self.image_tool.image("shou.png", click_times=2)
        self.action.click(20, 20)
        self.action.click(20, 20)

    def collect_task(self):
        clicks = [
            (410, -790),  # 寻求
            (-20, -770),  # 每日任务
            (330, -160),  # 全部接收
            (330, -160),  # 全部接收
            (150, -770),  # 周常任务
            (330, -160),  # 全部接收
            (330, -160),  # 全部接收
            (320, -770),  # 重复任务
            (330, -160),  # 全部接收
            (330, -160),  # 全部接收
            (330, -160),  # 全部接收
            (330, -160)  # 全部接收
        ]
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.action.click(20, 20)
        self.action.click(20, 20)

    def collect_bag(self):
        self.action.click(149,1021)  # 背包
        self.action.click(43,483)  # 箱子

        for _ in range(6):
            self.action.click(65, 569)  # 第一个物品
            self.action.click(334, 358), time.sleep(2)  # 使用
            if self.image_tool.image("que_green.png"):
                time.sleep(10)
                self.action.click(65, 569), time.sleep(2)  # 确认
            else:
                break
        self.action.click(20, 20)


    def toyz(self):
        self.log.info("放置Toyz")
        self.image_tool.image("ling.png", click_times=2)  # 领取奖励
        self.action.click(312,410)  # 放置ToyZ
        self.action.click(103,686), self.action.click(103,686)  #  选取第0个
        self.action.click(302,357)  # 放置第0个
        self.action.click(202,688), self.action.click(202,688)  # 选取第1个
        self.action.click(202,355)  # 放置第1个
        self.action.click(300,689), self.action.click(300,689)  # 选取第2个
        self.action.click(252,280)  # 放置第2个
        self.action.click(405,687), self.action.click(405,687)  # 选取第3个
        self.action.click(350,280)  # 放置第3个
        self.action.click(501,687), self.action.click(501,687)  # 选取第4个
        self.action.click(397,358)  # 放置第4个
        self.action.click(152,762), self.action.click(152,762)  # 选取第5个
        self.action.click(352,432)  # 放置第5个
        self.action.click(253,758), self.action.click(253,758)  # 选取第6个
        self.action.click(252,427)  # 放置第6个

        self.action.click(391,1006)  # 确认
        self.action.click(298,577)  # 开始
        self.action.click(20, 20)  # 返回主界面

    def underground(self):
        self.log.info("清理地下城")
        self.image_tool.image("bag.png", offset=(160, -170), click_times=2)  # 扫
        self.action.drag((360, 800), (360, 400))
        self.image_tool.image("bag.png", offset=(160, -170), click_times=2)  # 扫
        self.action.click(20, 20)
        self.action.click(20, 20)


    def task_24(self):
        self.log.info("领每日免费宝石")
        clicks = [
            (400, 0),  # 商店
            (200, 0),  # 套餐商店
            (-60, -610),  # 日常套餐
            (140, -575),  # Free
            (240, -325),  # 购买
            (160, -415),  # 确认
            (-100, 0)  # X
        ]
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.action.click(20, 20)
        self.action.click(20, 20)


        self.log.info("罗马竞技场")
        clicks = [
            (100, 0),  # 战斗
            (200, -75),  # 地下城
            (0, -770),  # 单人地下城
            (235, -475)  # 战斗准备
        ]
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        if not self.image_tool.image("0l1.png", click_times=0):
            self.image_tool.image("ru.png")
            for _ in range(10):
                if self.image_tool.image("chong.png"):
                    break
                time.sleep(10)
            for _ in range(10):
                if self.image_tool.image("que.png"):
                    break
                time.sleep(10)
        self.action.click(20, 20)
        self.action.click(20, 20)


    def task_12(self):
        self.log.info("领取任务奖励")
        self.collect_task()

        self.log.info("领取邮件")
        self.collect_mail()

        self.log.info("领取背包物品")
        self.collect_bag()

        self.log.info("打团队副本")
        clicks = [
            (100, 0),  # 战斗
            (360, -80),  # 团队副本
            (340, -500),  # 入口
            (100, 0)  # 战斗
        ]
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)

    def task_5(self):
        self.log.info("领AFK奖励")
        clicks = [
            (410, -665),  # 左箭头
            (265, -795),  # AFK
            (60, -300),  # 获得奖励
            (60, -300)   # 获得奖励
        ]
        base_position = self.image_tool.image("bag.png", click_times=0)
        if base_position is None:
            print("无法找到图像 'bag.png'")
            return False
        for offset in clicks:
            target_position = (base_position[0] + offset[0], base_position[1] + offset[1])
            self.action.click(*target_position)
        self.action.click(20, 20)
        self.action.click(20, 20)
        self.image_tool.image("bag.png", offset=(410, -665))





