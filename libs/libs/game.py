import random
import time
import libs.config as config
import os
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
        for remaining in range(seconds, -1, -1):
            print(f"\r{activity_name}: {remaining} 秒", end="")  # 显示倒计时在同一行
            time.sleep(1)  # 等待 1 秒
        print(f"\n")  # 换行并打印结束信息

    def esc(self, n=1):
        for _ in range(n):
            self.action.press("esc")
            time.sleep(2)
        self.action.click(210, 530)
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
        else:
            print("not in_game")
            self.window.open_window()
            return False

    def enter_afk(self, window_id):
        self.action.click(40, 275)  # 点击自动休眠
        if self.image_tool.text("镇"):
            self.image_tool.text("退出")
            self.choose_map()
            self.action.click(40, 275)  # 点击自动休眠
        self.switch_rarity(window_id)

    def wait_loaded(self, target, wait_time=60, load="picture", click_times=0, offset=(0, 0), region=None):
        """等待特定图像或文本加载"""
        elapsed_time = 0
        last_text_check_time = -10  # 用来记录上次检查文本的时间
        while elapsed_time < wait_time:
            if load == "picture":
                if self.image_tool.picture(target, offset=offset, click_times=click_times):  # 查找图片
                    print(f"{target} 图片已找到!")
                    time.sleep(2)  # 找到图片后，稍作暂停
                    return True  # 找到图片，立即返回
            elif load == "text":
                if elapsed_time - last_text_check_time >= 10:
                    if self.image_tool.text(target, offset=offset, click_times=click_times, region=region):  # 查找文本
                        print(f"{target} 文本已找到!")
                        time.sleep(2)  # 找到文本后，稍作暂停
                        return True  # 找到文本，立即返回
                    last_text_check_time = elapsed_time  # 更新上次检查时间

            # 如果没有找到，继续等待
            print(f"等待 {target} ... ({elapsed_time}/{wait_time} 秒)")

            time.sleep(1)  # 每秒检查一次
            elapsed_time += 1  # 每次检查后增加 elapsed_time

        # 如果超时
        print(f"未能在规定时间内找到 {target}，退出。")
        return False

    def enter_game(self, timeout=300):
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.in_game() or self.in_afk():
                result = self.image_tool.text("服务器的")
                if result is not None:
                    self.log.info("掉线")
                    x, y = result
                    self.action.click(x, y + 100)
                    self.action.click(x, y + 165)
                    self.timer(60, "等待重连进游戏")
                else:
                    print("成功进入游戏")
                    return True
            else:
                if self.image_tool.picture("PHA"):
                    self.timer(60, "等待进游戏")
                self.check_offline()
            print(f"等待进入游戏... ({elapsed_time}/{timeout} 秒)")
            time.sleep(15)
            elapsed_time += 15

        print(f"等待 {timeout} 秒后仍未进入游戏，结束检查,关闭窗口。")
        self.window.close_window()
        self.log.info(f"窗口已强制关闭")

    def handle_dialog(self):
        if self.in_afk():
            return
        self.timer(15, "等待弹窗加载")
        if self.wait_loaded("He", wait_time=10, load="text"):
            self.esc(2)
            for _ in range(3):
                result = self.wait_loaded("He", wait_time=10, load="text")
                if result:
                    self.action.press("esc")
                else:
                    break
            self.image_tool.text("确认", click_times=2)
            self.image_tool.text("月度签到", offset=(0, 470), click_times=3)
            self.image_tool.text("获得奖励", click_times=2)
            self.image_tool.text("确认", click_times=2)
            self.image_tool.text("获得奖励", click_times=2)
        self.esc(2)

    def check_offline(self):
        print("check_offline")
        result = self.image_tool.text("服务器的")
        if result is not None:
            self.log.info("掉线")
            x, y = result
            self.action.click(x, y + 100)
            self.action.click(x, y + 165)
            self.timer(60, "等待重连进游戏")
        if self.image_tool.text("下载"):
            self.log.info("游戏更新下载")
            self.wait_loaded("更新", wait_time=120, load="text", click_times=1, region=(0, 0, 150, 200))
            self.wait_loaded("玩", wait_time=120, load="text", click_times=1, region=(0, 0, 150, 200))
            self.wait_loaded("Additional data download", wait_time=15, offset=(0, 140), click_times=1, load="text")
        self.image_tool.text("Additional data download", offset=(0, 140))
        if self.image_tool.text("维护", click_times=0):
            self.log.info("游戏维护")
            self.window.close_window()
            self.timer(600, "等待维护。。。")


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

        found_color = False
        for _ in range(20):
            coordinates = [(323, 611)]
            purple = (108, 55, 158)
            orange = (173, 87, 62)
            tolerance = 25

            # 打印坐标进行调试
            print(f"检查坐标：{coordinates}")

            result1 = self.image_tool.color(coordinates, orange, tolerance)
            if result1:
                print("找到橙色")
                found_color = True
                self.image_tool.picture("X")
                self.image_tool.picture("bag", offset=(2 * 77, -400))  # 固定位置的一件装备

                # 检查装备是否需要加入收藏
                self.image_tool.picture("bag", offset=(370, -140))  # 收藏快捷方式
                # 判断是否需要点击空白处或红色亮点，检查装备是否需要加入收藏
                if self.image_tool.picture("knife_without_spot", threshold=0.94):  # 未找到需要加入图鉴的装备
                    time.sleep(1)
                    if self.image_tool.text("攻击力"):
                        self.image_tool.picture("knife_without_spot", threshold=0.94)
                        self.image_tool.picture("knife", offset=(0, -120))  # 随便点击空白处
                        # 暂时将装备材料化，等待升级或卖掉
                        self.image_tool.picture("bag", offset=(230, -140))  # 设备材料化
                        self.image_tool.picture("bag", offset=(240, -350), click_times=2)  # 确认
                        time.sleep(2)
                    self.image_tool.picture("knife_without_spot", threshold=0.94)
                    self.image_tool.picture("knife", offset=(0, -120))  # 随便点击空白处
                    # 分解装备
                    print("分解装备")
                    result = self.image_tool.picture("salvage")
                    if result is not None:
                        x, y = result
                        self.action.click(x + 200, y + 110)  # 分解
                        self.action.click(x + 190, y - 265)  # 确认
                        self.action.click(x + 190, y - 265)  # 确认

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
                        if not self.image_tool.text("攻击力"):
                            self.image_tool.picture("knife")
                            self.image_tool.picture("knife", offset=(0, -150))
                            print("分解装备")
                            result = self.image_tool.picture("salvage")
                            if result is not None:
                                x, y = result
                                self.action.click(x + 200, y + 110)  # 分解
                                self.action.click(x + 190, y - 265)  # 确认
                                self.action.click(x + 190, y - 265)  # 确认
                                time.sleep(2)
                        else:
                            self.image_tool.picture("knife")
                            self.image_tool.picture("knife", offset=(0, -150))
                            # 暂时将装备材料化，等待升级或卖掉
                            self.image_tool.picture("bag", offset=(230, -140))  # 设备材料化
                            self.image_tool.picture("bag", offset=(240, -350), click_times=2)  # 确认
                            time.sleep(2)

            result2 = self.image_tool.color(coordinates, purple, tolerance)
            if result2:
                print("找到紫色")
                found_color = True
                self.image_tool.picture("X")
                self.image_tool.picture("bag", offset=(2 * 77, -400))  # 固定位置的一件装备

                # 检查装备是否需要加入收藏
                self.image_tool.picture("bag", offset=(370, -140))  # 收藏快捷方式
                # 判断是否需要点击空白处或红色亮点，检查装备是否需要加入收藏
                if self.image_tool.picture("knife_without_spot", threshold=0.94, click_times=0):  # 未找到需要加入图鉴的装备
                    self.image_tool.picture("knife", offset=(0, -120))  # 随便点击空白处
                    # 分解装备
                    print("分解装备")
                    result = self.image_tool.picture("salvage")
                    if result is not None:
                        x, y = result
                        self.action.click(x + 200, y + 110)  # 分解
                        self.action.click(x + 190, y - 265)  # 确认
                        self.action.click(x + 190, y - 265)  # 确认
                        time.sleep(2)
                else:  # 该装备需要收藏
                    result = self.image_tool.picture("knife")
                    if result is not None:
                        x2, y2 = result
                        self.action.drag((x2, y2 + 390), (x2, y2+25))  # 拖拽到下一页
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
                        result = self.image_tool.picture("salvage")
                        if result is not None:
                            x, y = result
                            self.action.click(x + 200, y + 110)  # 分解
                            self.action.click(x + 190, y - 265)  # 确认
                            self.action.click(x + 190, y - 265)  # 确认
                            time.sleep(2)

            if not found_color:
                print("未找到紫色或橙色")
                break

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
                        time.sleep(1)
                        break

    def switch_rarity(self, window_id):
        self.image_tool.text("自动技能")
        text_list = ["稀有", "史诗", "关闭", "普通"]
        # 检查目标图像是否在列表中
        target_text = config.afk(window_id)
        if target_text not in text_list:
            print(f"错误：目标文字 {target_text} 不在有效文字列表中。")
            return False
        for _ in range(3):
            for text in text_list:
                coords = self.image_tool.text(text, click_times=0, region=(0, 600, 580, 400))  # 获取文字的坐标
                if coords:  # 如果找到了当前文字
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
        land_key = str(map_code)[0]  # 图片编号
        level = int(str(map_code)[1])  # 关卡编号

        # 获取图片名和基础偏移值
        map_num = map_info.get(land_key)
        if map_num is None:
            raise ValueError(f"Invalid map_key: {land_key}")

        land, base_offset_x = map_num

        # 计算最终偏移值：每个关卡增加 80 的偏移
        offset_x = base_offset_x * level
        offset_y = 0  # 偏移 Y 默认固定为 0

        # 检查是否在战斗中
        self.image_tool.text("退出")
        # 执行地图切换操作
        self.switch_auto("auto_red")
        self.image_tool.picture("bag", offset=(100, 0))  # 点击战斗
        time.sleep(2)
        self.image_tool.picture("bag", offset=(-40, -70))  # 点击场地
        time.sleep(3)
        self.action.click(130, 225)
        self.action.click(130, 225)
        time.sleep(3)
        if 4 < int(land_key) < 9:
            self.image_tool.picture("bag", offset=(130, -750)), time.sleep(2)
        if 8 < int(land_key) < 13:
            self.image_tool.picture("bag", offset=(130, -750)), time.sleep(2)
            self.action.drag((100, 760), (100, 100)), time.sleep(2)
        self.image_tool.picture(land, offset=(offset_x, offset_y))
        self.esc(2)
        # 根据 level 打印不同的日志信息
        if level == 0:  # 回城镇
            print(f"{self.window.window_id} 回城")
        else:  # 其他关卡
            print(f"{self.window.window_id} 去往地图 {map_info[land_key][0]}, 第 {level} 关")
        self.wait_loaded("ruby")
        time.sleep(3)


    def collect_diamond(self):
        for _ in range(3):
            self.image_tool.picture("100%", threshold=0.8, click_times=2)
        if (self.image_tool.text("升级")
            or self.image_tool.text("设备拆装")):
            self.image_tool.picture("bag", offset=(-100, 0))
            for i in range(1, 7):
                self.book(i)
            self.image_tool.text("成长")
            self.image_tool.text("升级", click_times=3)
            self.esc()
        self.image_tool.picture("100%", threshold=0.8, click_times=3)

    def move_in_party_dungeon(self):
        self.action.press("A", second=6)
        self.action.press("W", second=6)

        self.action.press("S", second=5)
        self.action.press("D", second=5)
        time.sleep(1)
        self.action.press("W", second=4)
        self.action.press("A", second=4)
        time.sleep(1)

        self.action.press("S", second=3)
        self.action.press("D", second=3)
        self.action.press("W", second=2)
        self.action.press("A", second=2)


    def boss(self):
        print("进入boss")
        self.wait_loaded("dungeon")

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
        max_time = 5 * 60  # 最大运行时间为5分钟
        start_time = time.time()  # 记录函数开始时间

        for _ in range(15):
            for _ in range(10):
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

            if not self.wait_loaded("dungeon", wait_time=5):
                if (self.image_tool.text("移动到下一个区域", click_times=3)
                        or self.image_tool.text("逃脱")):
                    time.sleep(2)
                    self.wait_loaded("ruby")
                    time.sleep(3)
                    self.image_tool.text("消除", offset=(175, 0))
                    self.esc()
                    self.switch_auto("auto_red")
                    break

                self.move_in_party_dungeon()
                self.image_tool.picture("exit")
                self.image_tool.text("口")
                break

            # 检查是否超过最大运行时间
            if time.time() - start_time > max_time:
                print("超出最大时间限制，退出函数")
                self.esc()
                self.switch_auto("auto_red")
                return

        self.switch_auto("auto_red")





















