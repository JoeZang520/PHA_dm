import random
import time
import libs.config as config
import sys

class Game:
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

    def in_game(self):
        if self.window.game_exist() and self.window.bind_window():
            if self.image_tool.picture("ruby", click_times=0):
                print("in_game")
                return True
        else:
            print("not in_game")
            self.window.open_window()
            return False

    def in_afk(self):
        if self.window.game_exist() and self.window.bind_window():
            if self.image_tool.text("装备自动分解", click_times=0):
                print("in_afk")
                return True
        else:
            print("not in_afk")
            return False
        
    def in_fight(self):
        if self.in_game():
            if self.image_tool.picture("auto_red", click_times=0):
                print("in_fight")
                return True
            else:
                print("not in_fight")
                return False
            
    def wait_page_loaded(self, timeout=60):
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.image_tool.picture("ruby", click_times=0):
                return
            print(f"等待加载画面... ({elapsed_time}/{timeout} 秒)")
            time.sleep(1)  # 每秒检查一次
            elapsed_time += 1


    def enter_game(self, timeout=150):
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.image_tool.picture("maintain", click_times=0):
                self.log.info("游戏维护")
                self.window.close_window()
                sys.exit(1)
            if self.in_game() or self.in_afk():  # 如果已经进入游戏
                print("成功进入游戏")
                return
            print(f"等待进入游戏... ({elapsed_time}/{timeout} 秒)")
            time.sleep(10)  # 每秒检查一次
            elapsed_time += 10

        # 如果 60 秒内没进入游戏，结束函数，不报错
        print(f"等待 {timeout} 秒后仍未进入游戏，结束检查,关闭窗口。")
        self.window.close_window()

    def handle_dialog(self):
        self.check_offline()
        self.image_tool.picture("PHA")
        if not self.in_afk():
            self.timer(10, "等待弹窗加载")
            for _ in range(3):
                self.image_tool.text("Pixel", offset=(260, 0))
                time.sleep(3)
            self.image_tool.text("确认", click_times=2)
            self.image_tool.text("月度签到", offset=(0, 470), click_times=3)
            self.image_tool.text("获得奖励", click_times=2)
            self.image_tool.text("确认", click_times=2)
            self.image_tool.text("获得奖励", click_times=2)
        self.esc()

    def check_offline(self):
        print("check_offline")
        result = self.image_tool.text("与服务器的连接已丢失。")
        if result is not None:
            self.log.info("网络错误")
            x , y = result
            self.action.click(x, y + 100)
            self.action.click(x, y + 165)
            self.timer(60, "等待重连进游戏")
        if self.image_tool.text("下载"):
            self.log.info("游戏更新下载")
            self.timer(15, "等待额外数据包")
            self.image_tool.text("Additional data download", offset=(0, 140))
            self.timer(60, "等待下载")
        if self.image_tool.text("Additional data download", offset=(0, 140)):
            self.log.info("游戏更新下载")
            self.timer(60, "等待下载")

    # 将装备加入图鉴或者分解
    def book(self, equip_number):
        # 初始点击项
        x_offset = -110 + (equip_number - 1) * 55  # 根据 equip_number 动态计算 x 坐标
        clicks = [
            (40, -70, "装备"),
            (x_offset, -475, f"装备物品{equip_number}"),  # 动态设置装备物品的 x 坐标
            (275, -475, "排序")
        ]

        # 先执行固定的点击项
        result = self.image_tool.picture("bag", click_times=0)
        if result is None:
            print("无法找到图像 'bag'")
            return False
        x, y = result

        # 执行初始点击项
        for offset in clicks:
            x_offset, y_offset, label = offset
            target_position = (x + x_offset, y + y_offset)
            self.action.click(*target_position)
            print(f"点击 {label} : {target_position}")

        for _ in range(20):
            coordinates = [(x - 30 + 3 * 77, y - 368), (x - 10 + 3 * 77, y - 368), (x + 20 + 3 * 77, y - 368)]
            purple = (108, 55, 158)
            orange = (173, 87, 62)
            tolerance = 25

            # 打印坐标进行调试
            print(f"检查坐标：{coordinates}")

            result1 = self.image_tool.color(coordinates, orange, tolerance)
            if result1:
                print("找到橙色")
                self.image_tool.picture("X")
                self.image_tool.picture("bag", offset=(3 * 77, -400))  # 固定位置的一件装备

                # 检查装备是否需要加入收藏
                self.image_tool.picture("bag", offset=(370, -140))  # 收藏快捷方式
                # 判断是否需要点击空白处或红色亮点，检查装备是否需要加入收藏
                if self.image_tool.picture("knife_without_spot", threshold=0.95):  # 未找到需要加入图鉴的装备
                    time.sleep(1)
                    if self.image_tool.text("攻击力+"):
                        self.image_tool.picture("knife_without_spot", threshold=0.95)
                        self.image_tool.picture("knife", offset=(0, -120))  # 随便点击空白处
                        # 暂时将装备材料化，等待升级或卖掉
                        self.image_tool.picture("bag", offset=(230, -140))  # 设备材料化
                        self.image_tool.picture("bag", offset=(240, -350), click_times=2)  # 确认
                        time.sleep(2)
                else:  # 该装备需要收藏
                    result = self.image_tool.picture("knife")
                    if result is not None:
                        x1, y1 = result
                        # 点击查找需未加入图鉴的装备
                        base_x1 = x1 - 150
                        base_y1 = y1 + 120
                        offset = 70  # 每次偏移的量
                        # 循环进行点击操作
                        for i in range(3):  # 偏移三次
                            self.action.click(base_x1 + i * offset, base_y1)
                            if self.image_tool.text("收藏增益登记", offset=(20, 60)):
                                self.image_tool.text("选择")
                                self.image_tool.text("确认", click_times=2)
                        if not not self.image_tool.text("攻击力+"):
                            self.image_tool.picture("knife")
                            self.image_tool.picture("knife", offset=(0, -120))
                            print("分解装备")
                            if self.image_tool.picture("salvage"):
                                self.image_tool.picture("ruby", offset=(130, 930))  # 分解
                                self.image_tool.picture("ruby", offset=(120, 550), click_times=2)  # 确认
                        else:
                            # 暂时将装备材料化，等待升级或卖掉
                            self.image_tool.picture("bag", offset=(230, -140))  # 设备材料化
                            self.image_tool.picture("bag", offset=(240, -350), click_times=2)  # 确认
                            time.sleep(2)

            result2 = self.image_tool.color(coordinates, purple, tolerance)
            if result2:
                print("找到紫色")
                self.image_tool.picture("X")
                self.image_tool.picture("bag", offset=(3 * 77, -400))  # 固定位置的一件装备

                # 检查装备是否需要加入收藏
                self.image_tool.picture("bag", offset=(370, -140))  # 收藏快捷方式
                # 判断是否需要点击空白处或红色亮点，检查装备是否需要加入收藏
                if self.image_tool.picture("knife_without_spot", threshold=0.95, click_times=0):  # 未找到需要加入图鉴的装备
                    self.image_tool.picture("knife", offset=(0, -120))  # 随便点击空白处
                    # 分解装备
                    print("分解装备")
                    if self.image_tool.picture("salvage"):
                        self.image_tool.picture("ruby", offset=(130, 930))  # 分解
                        self.image_tool.picture("ruby", offset=(120, 550), click_times=2)  # 确认
                else:  # 该装备需要收藏
                    result = self.image_tool.picture("knife")
                    if result is not None:
                        x2, y2 = result
                        self.action.drag((x2, y2 + 320), (x2, y2))  # 拖拽到下一页
                        time.sleep(1)

                        # 点击查找需未加入图鉴的装备
                        base_x = x2 - 150
                        base_y = y2 + 370
                        offset = 70  # 每次偏移的量
                        # 循环进行点击操作
                        for i in range(3):  # 偏移三次
                            self.action.click(base_x + i * offset, base_y)
                            if self.image_tool.text("收藏增益登记", offset=(20, 60)):
                                self.image_tool.text("选择")
                                self.image_tool.text("确认", click_times=2)
                        self.action.drag((80, 600), (80, 1200))  # 拖拽回首页
                        self.image_tool.picture("knife")
                        self.image_tool.picture("knife", offset=(0, -120))
                        print("分解装备")
                        if self.image_tool.picture("salvage"):
                            self.image_tool.picture("ruby", offset=(130, 930))  # 分解
                            self.image_tool.picture("ruby", offset=(120, 550), click_times=2)  # 确认

            else:
                break
        self.image_tool.picture("100%", threshold=0.8, click_times=3)


    # 分解装备
    def salvage_equip(self, rarity, window_id):
        if self.config.afk(window_id):
            return
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


    def grow(self):
        clicks = [
            (-100, 0),  # 人物
            (-80, -75),  # 成长
            (290, -650),  # 升级
            (290, -650),  # 升级
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

    def switch_auto(self, target_image):
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

    def switch_rarity(self, window_id):
        text_list = ["稀有", "史诗", "关闭", "普通"]
        # 检查目标图像是否在列表中
        target_text = config.afk(window_id)
        if target_text not in text_list:
            print(f"错误：目标图像 {target_text} 不在有效文字列表中。")
            return False
        for _ in range(3):
            for text in text_list:
                coords = self.image_tool.text(text, click_times=0)  # 获取图片的坐标
                if coords:  # 如果找到了当前图像
                    if text == target_text:
                        return True
                    else:
                        self.action.click(*coords)
                        break

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

        map_code = config.map_code(self.window.window_id)

        # 获取图片编号和关卡编号
        image_key = str(map_code)[0]  # 图片编号
        level = int(str(map_code)[1])  # 关卡编号

        # 获取图片名和基础偏移值
        map_num = map_info.get(image_key)
        if map_num is None:
            raise ValueError(f"Invalid map_key: {image_key}")

        image, base_offset_x = map_num

        # 计算最终偏移值：每个关卡增加 80 的偏移
        offset_x = base_offset_x * level
        offset_y = 0  # 偏移 Y 默认固定为 0

        # 检查是否在战斗中
        if not self.in_afk():
            # 执行地图切换操作
            self.switch_auto("auto_red")
            self.image_tool.picture("bag", offset=(100, 0))  # 点击战斗
            self.image_tool.picture("bag", offset=(-40, -70))  # 点击场地
            if 4 < int(image_key) < 9:
                self.image_tool.picture("bag", offset=(130, -750)), time.sleep(2)
            if 8 < int(image_key) < 13:
                self.image_tool.picture("bag", offset=(130, -750)), time.sleep(2)
                self.action.drag((100, 760), (100, 100)), time.sleep(2)
            self.image_tool.picture(image, offset=(offset_x, offset_y))
            self.action.click(20, 20)
            self.action.click(20, 20)
            # 根据 level 打印不同的日志信息
            if level == 0:  # 回城镇
                print(f"{self.window.window_id} 回城")
            else:  # 其他关卡
                print(f"{self.window.window_id} 去往地图 {map_info[image_key][0]}, 第 {level} 关")
            self.wait_page_loaded()

    def collect_diamond(self):
        for _ in range(3):
            self.image_tool.picture("100%", threshold=0.8, click_times=2)

        self.image_tool.picture("bag", offset=(-100,0))
        for i in range(1, 7):
            self.book(i)
        self.image_tool.picture("bag", offset=(-100, 0))
        self.grow()



    def boss(self):
        self.wait_page_loaded()
        time.sleep(1)
        self.switch_auto("auto_green")

        directions = [
            ("W",),  # 上
            ("S",),  # 下
            ("A",),  # 左
            ("D",),  # 右
            ("W", "A"),  # 左上
            ("W", "D"),  # 右上
            ("S", "A"),  # 左下
            ("S", "D"),  # 右下
        ]

        last_direction = None  # 记录上一次的方向
        extra_rounds = 0  # 记录额外执行的轮数
        confirm = False  # 是否找到确定
        last_check_time = time.time()

        for _ in range(50):
            if time.time() - last_check_time > 20:  # 每隔20秒检查一次
                last_check_time = time.time()
                if (self.image_tool.text("移动到下一个区域", click_times=3)
                        or self.image_tool.text("逃脱")):
                    self.wait_page_loaded()
                    self.switch_auto("auto_red")
                    return
                if self.image_tool.text("确定"):
                    if not confirm:  # 如果第一次找到
                        confirm = True  # 设置已找到
                        extra_rounds = 5  # 找到后设置额外的执行轮数


            # 如果执行了额外的轮数，继续执行
            if extra_rounds > 0:
                extra_rounds -= 1

            # 排除与上一次方向完全重复或部分重复的方向
            if last_direction:
                valid_directions = [
                    d for d in directions
                    if not any(key in last_direction for key in d)  # 排除与上次方向有重复按键的方向
                ]
            else:
                valid_directions = directions  # 如果是第一次，则使用所有方向

            # 如果排除后没有方向可用（极端情况下），重置为所有方向
            if not valid_directions:
                valid_directions = directions

            # 随机选择一个方向
            direction = random.choice(valid_directions)

            # 生成随机时间，控制步长
            if len(direction) == 1:  # 单方向
                steps = random.uniform(2, 3) if direction[0] in ["A", "D"] else random.uniform(2, 3)
            else:  # 斜线方向（步长稍短，以更精准覆盖区域）
                steps = random.uniform(3, 4)

            # 执行按键（支持单方向和双方向）
            self.action.press(*direction, second=steps)

            # 更新上一次的方向
            last_direction = direction

            # 如果已执行了 5 轮额外操作且图片已找到，退出循环
            if extra_rounds == 0 and confirm:
                break

        self.switch_auto("auto_red")

















