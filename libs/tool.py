import os
import subprocess
import time
import ctypes
import cv2
import numpy as np
import win32com.client
from PIL import Image
import win32gui
import win32con
import requests
import base64
import io


class Window:
    def __init__(self, window_id):
        self.window_id = window_id
        self.instance_mapping = {
            "001": "Pie64_1",
            "002": "Pie64_2",
            "003": "Pie64_3",
        }
        self.package_name = "com.Z5.Adventure"
        self.instance_id = self.instance_mapping.get(window_id)
        if not self.instance_id:
            raise ValueError(f"未知的 window_id '{window_id}'，请检查实例映射。")

        # 加载大漠插件并创建实例
        obj = ctypes.windll.LoadLibrary(r"C:\Users\J9\Desktop\PHA_dm\DmReg.dll")
        obj.SetDllPathW(r"C:\Users\J9\Desktop\PHA_dm\dm.dll")
        self.dm = win32com.client.Dispatch('dm.dmsoft')
        self.hwnd = None
        self.game_hwnd = None
        self.action = Action(self)  # 创建 Action 对象并传递当前窗口实例

        # 注册大漠插件
        self.register_dm_plugin()

        # 默认情况下绑定窗口
        self.is_bound = False

    def register_dm_plugin(self):
        """注册大漠插件"""
        try:
            res = self.dm.reg("mh84909b3bf80d45c618136887775ccc90d27d7", "mimhwsaelcfp20vf7")
            if res == 1:
                print("大漠插件注册成功")
            else:
                print("大漠插件注册失败")
        except Exception as e:
            print(f"注册大漠插件失败: {e}")

    def get_hwnd(self):
        """获取父窗口句柄"""

        def enum_windows_callback(hwnd, hwnd_list):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd).strip()
                if self.window_id in window_title:
                    hwnd_list.append(hwnd)

        hwnd_list = []
        win32gui.EnumWindows(enum_windows_callback, hwnd_list)

        if hwnd_list:
            return hwnd_list[0]
        else:
            return None

    def get_child_hwnd(self, parent_hwnd):
        """获取父窗口的子窗口句柄"""
        child_hwnds = []

        def enum_child_windows(hwnd, child_hwnds):
            if win32gui.IsWindowVisible(hwnd):
                child_hwnds.append(hwnd)

        win32gui.EnumChildWindows(parent_hwnd, enum_child_windows, child_hwnds)
        return child_hwnds

    def bind_window(self):
        """绑定游戏窗口"""
        # 如果已经绑定，直接返回
        if self.is_bound:
            print(f"游戏窗口 '{self.window_id}' 已经绑定")
            return True

        # 获取父窗口句柄
        parent_hwnd = self.get_hwnd()
        if not parent_hwnd:
            print(f"未能找到父窗口句柄: {self.window_id}")
            return False

        # 获取父窗口的子窗口句柄（假设游戏窗口是子窗口）
        child_hwnds = self.get_child_hwnd(parent_hwnd)
        if not child_hwnds:
            print(f"未能找到子窗口")
            return False

        # 假设第一个子窗口是游戏窗口，或者根据子窗口的其他特征来选择
        game_hwnd = child_hwnds[0]
        print(f"找到游戏窗口句柄: {game_hwnd}")

        # 绑定游戏窗口
        res = self.dm.BindWindow(game_hwnd, "normal", "windows2", "windows", 0)
        if res == 1:
            print(f"游戏窗口 '{self.window_id}' 绑定成功")
            self.hwnd = game_hwnd
            self.is_bound = True  # 标记为已绑定
            return True
        else:
            print(f"游戏窗口 '{self.window_id}' 绑定失败")
            return False

    def open_window(self, timeout=60):
        bluestacks_path = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"

        cmd_args = [
            bluestacks_path,
            "--instance", self.instance_id,  # 使用实例 ID
            "--cmd", "launchAppWithBsx",
            "--package", self.package_name,
            "--source", "desktop_shortcut"
        ]

        # 检查窗口句柄是否已经存在
        self.hwnd = self.get_hwnd()
        if self.hwnd:
            print(f"窗口 '{self.window_id}' 已经存在，句柄: {self.hwnd}")
            return True

        try:
            subprocess.Popen(cmd_args, shell=False)
            print(f"正在启动窗口 '{self.window_id}'")
        except Exception as e:
            print(f"启动 BlueStacks 实例失败: {e}")
            return False

        # 等待窗口加载
        elapsed_time = 0
        while elapsed_time < timeout:
            self.hwnd = self.get_hwnd()
            if self.hwnd:
                print(f"窗口 '{self.window_id}' 加载成功，句柄: {self.hwnd}")
                return True
            print(f"未找到窗口 '{self.window_id}' 的句柄，等待加载中... ({elapsed_time}/{timeout} 秒)")
            time.sleep(1)
            elapsed_time += 1

        print(f"窗口 '{self.window_id}' 加载超时，请检查模拟器状态。")
        return False

    def close_window(self):
        """通过父窗口句柄关闭窗口"""
        # 获取父窗口句柄
        parent_hwnd = self.get_hwnd()
        if not parent_hwnd:
            print(f"未能找到父窗口句柄: {self.window_id}")
            return False

        try:
            # 发送关闭请求
            res = win32gui.PostMessage(parent_hwnd, win32con.WM_CLOSE, 0, 0)
            if res:
                print(f"窗口 '{self.window_id}' 关闭请求已发送")
                return True
            else:
                print(f"窗口 '{self.window_id}' 关闭失败")
                return False
        except Exception as e:
            print(f"关闭窗口失败: {e}")
            return False

    def capture_window(self, region=None):
        """截取窗口内容"""
        if not self.is_bound:
            if not self.bind_window():
                print("绑定失败，无法执行点击操作")
                return

        # 获取窗口的客户端区域坐标
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        width = right - left  # 截取区域的宽度
        height = bottom - top  # 截取区域的高度

        # 如果提供了 region 参数，则使用指定区域的坐标和大小
        if region:
            x1, y1, w, h = region
            left = left + x1  # 相对窗口的左上角坐标
            top = top + y1
            width = w
            height = h

        hdc = win32gui.GetDC(self.hwnd)
        mem_dc = win32gui.CreateCompatibleDC(hdc)
        bitmap = win32gui.CreateCompatibleBitmap(hdc, width, height)

        win32gui.SelectObject(mem_dc, bitmap)
        win32gui.BitBlt(mem_dc, 0, 0, width, height, hdc, left, top, win32con.SRCCOPY)

        bmp_header = win32gui.GetObject(bitmap)
        buffer_size = bmp_header.bmWidthBytes * bmp_header.bmHeight
        bits = ctypes.create_string_buffer(buffer_size)

        hdc_win32 = ctypes.windll.gdi32.GetBitmapBits
        hdc_win32.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        hdc_win32(bitmap.handle, buffer_size, bits)

        img = Image.frombuffer('RGB', (bmp_header.bmWidth, bmp_header.bmHeight), bits, 'raw', 'BGRX', 0, 1)

        # 将左上角100x100区域的像素设置为黑色（这部分可以去掉或根据需求修改）
        img.paste((0, 0, 0), (0, 0, 100, 30))  # 设置左上角区域为黑色

        win32gui.DeleteObject(bitmap)
        win32gui.DeleteDC(mem_dc)
        win32gui.ReleaseDC(self.hwnd, hdc)

        return img


class Action:
    def __init__(self, window):
        self.window = window

    def click(self, x, y, click_times=1):
        """模拟点击"""
        # 检查是否已经绑定
        if not self.window.is_bound:
            if not self.window.bind_window():
                print("绑定失败，无法执行点击操作")
                return  # 绑定失败则不执行点击操作

        # 使用大漠插件将鼠标移动到指定位置并点击
        dm = self.window.dm
        dm.MoveTo(x, y)  # 移动到指定坐标
        for _ in range(click_times):
            dm.LeftClick()  # 执行点击操作
            # print(f"点击{x, y}")

        # 添加延迟，确保操作完成（你可以根据需要调整延迟）
        time.sleep(1.5)

    def press(self, *keys, second=None):
        """
        模拟键盘按键操作，支持同时按下多个键
        :param keys: 字符，例如 "A", "W"，或者特殊键名，例如 "ESC"
        :param second: 按住按键的时间（如果未传递时间，默认为0.1秒）
        """
        if second is None:
            # 如果未传递 `second` 参数，则取最后一个非字符串参数为时间
            if len(keys) > 0 and isinstance(keys[-1], (int, float)):
                second = keys[-1]  # 将最后一个非字符串参数视为时间
                keys = keys[:-1]  # 移除时间参数，只保留按键
            else:
                second = 0.1  # 默认按键时间

        # 转换按键为大写
        keys = [key.upper() for key in keys if isinstance(key, str)]

        # 定义字符到虚拟键码（VK）的映射
        char_to_vk = {
            "A": 0x41, "B": 0x42, "C": 0x43, "D": 0x44, "E": 0x45,
            "F": 0x46, "G": 0x47, "H": 0x48, "I": 0x49, "J": 0x4A,
            "K": 0x4B, "L": 0x4C, "M": 0x4D, "N": 0x4E, "O": 0x4F,
            "P": 0x50, "Q": 0x51, "R": 0x52, "S": 0x53, "T": 0x54,
            "U": 0x55, "V": 0x56, "W": 0x57, "X": 0x58, "Y": 0x59, "Z": 0x5A,
            "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
            "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
            "ESC": 0x1B
        }

        # 验证按键是否有效
        vk_codes = []
        for key in keys:
            if key not in char_to_vk:
                print(f"不支持的按键：{key}")
                return
            vk_codes.append(char_to_vk[key])

        # 使用大漠插件进行按键操作
        if not self.window.is_bound:
            if not self.window.bind_window():
                return  # 绑定失败则不执行点击操作
        dm = self.window.dm

        # 按下所有按键
        for key_code in vk_codes:
            dm.keydown(key_code)  # 按下键
            print(f"按键 {keys}")

        # 按住按键的时间
        time.sleep(second)

        # 释放所有按键
        for key_code in vk_codes:
            dm.keyup(key_code)  # 释放键
        # time.sleep(0.5)

    def drag(self, start, end, duration=3.0, steps=100):
        """
        使用大漠插件模拟鼠标按住并滑动屏幕
        :param start: 起始位置的坐标元组 (x, y)
        :param end: 结束位置的坐标元组 (x, y)
        :param duration: 滑动总时间（秒）
        :param steps: 滑动的步骤数，值越大越平滑
        """
        if not self.window.is_bound:
            if not self.window.bind_window():
                return  # 绑定失败则不执行拖动操作

        dm = self.window.dm  # 获取大漠插件实例

        # 解包起始坐标和结束坐标
        start_x, start_y = start
        end_x, end_y = end

        # 计算每一步的滑动增量
        delta_x = (end_x - start_x) / steps
        delta_y = (end_y - start_y) / steps

        # 模拟鼠标按下
        dm.MoveTo(start_x, start_y)
        dm.LeftDown()  # 按下左键


        # 逐步滑动鼠标
        for i in range(steps + 1):
            current_x = int(start_x + delta_x * i)
            current_y = int(start_y + delta_y * i)
            dm.MoveTo(current_x, current_y)
            time.sleep(duration / steps)


        # 模拟鼠标释放
        dm.LeftUp()  # 释放左键
        time.sleep(0.5)



class ImageTool:
    def __init__(self, action):
        self.action = action

    def picture(self, png, threshold=0.8, offset=(0, 0), click_times=1, color=True):
        # 获取图片路径并加载图片
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 自动添加 ".png" 扩展名，如果没有提供扩展名
        if not png.endswith('.png'):
            png += '.png'

        target_path = os.path.join(base_dir, 'images', png)
        target = cv2.imread(str(target_path))

        if target is None:
            print(f"无法加载模板图片 '{png}'")
            return None

        # 确保模板图像为 uint8 类型
        target = target.astype('uint8')

        # 获取窗口截图
        screenshot = self.action.window.capture_window()
        if screenshot is None or screenshot.size == 0:
            print("窗口截图失败，无法进行匹配。")
            return None

        # 将截图转换为NumPy数组
        screenshot = np.array(screenshot)
        screenshot = screenshot.astype('uint8')  # 确保截图为 uint8 类型

        # 如果是彩色图像，转换为BGR
        if color:
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            if screenshot_bgr.shape[0] < target.shape[0] or screenshot_bgr.shape[1] < target.shape[1]:
                print(f"截图小于模板图片 '{png}'，无法进行模板匹配。")
                return None
            result = cv2.matchTemplate(screenshot_bgr, target, cv2.TM_CCOEFF_NORMED)
        else:
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)  # 添加这行将目标图像转换为灰度
            if screenshot_gray.shape[0] < target_gray.shape[0] or screenshot_gray.shape[1] < target_gray.shape[1]:
                print(f"截图小于模板图片 '{png}'，无法进行模板匹配。")
                return None
            result = cv2.matchTemplate(screenshot_gray, target_gray, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            target_height, target_width = target.shape[:2]
            center_x = max_loc[0] + target_width // 2
            center_y = max_loc[1] + target_height // 2

            x = center_x + offset[0]
            y = center_y + offset[1]

            print(f"找到图片 '{png}'，坐标({x}, {y})，偏移 {offset}，点击 {click_times} 次")
            for _ in range(click_times):
                self.action.click(x, y)
            return x, y
        else:
            print(f"未找到{png}")
            return None

    def color(self, coordinates, target_color, tolerance=10):
        """
        判断多个指定位置的颜色是否为目标颜色，只要一个匹配成功就返回True。
        :param coordinates: 坐标列表，包含多个 (x, y) 元组
        :param target_color: 目标颜色, 格式为 (R, G, B)
        :param tolerance: 容忍度，用于颜色匹配
        :return: True 如果有一个点颜色匹配，False 否则
        """
        # 获取窗口截图
        screenshot = self.action.window.capture_window()
        if screenshot is None or screenshot.size == 0:
            print("窗口截图失败，无法进行匹配。")
            return None

        # 将截图转换为NumPy数组
        screenshot = np.array(screenshot)
        screenshot = screenshot.astype('uint8')

        for x, y in coordinates:
            # 获取指定坐标的像素颜色
            pixel_color = screenshot[y, x]

            # 计算颜色差异
            diff = np.abs(np.array(pixel_color) - np.array(target_color))
            if np.all(diff <= tolerance):  # 如果颜色差异小于容忍度，认为颜色匹配
                return True
        return False

    def text(self, target_text, offset=(0, 0), click_times=1, region=None):
        """
        查找图片中的指定文字，并在找到目标文字时执行点击操作。

        参数:
        target_text: 目标文字
        offset: 偏移量
        click_times: 点击次数
        region: 限制识别区域，格式为 (x1, y1, width, height)
        """
        # 获取当前窗口的截图
        screenshot = self.action.window.capture_window(region=region)
        if screenshot is None:
            print("无法获取截图")
            return None

        # 将图片转换为 base64 编码
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # 向服务器发送 POST 请求进行 OCR 识别
        url = "http://127.0.0.1:20086/base64"
        res = requests.post(url, json={"img": img_base64})

        # 获取返回的 JSON 数据
        response_data = res.json()

        # 存储文字和坐标的列表
        text_coordinates = []

        # 提取识别到的文字和坐标信息
        if response_data["code"] == 1 and response_data["data"]:
            for item in response_data["data"]:
                text = item["text"]
                x1, y1, x2, y2 = item["x1"], item["y1"], item["x2"], item["y2"]

                # 计算中心点坐标
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                text_coordinates.append((text, (center_x, center_y)))
        else:
            print("未识别到任何文字。")
            return None

        # 计算坐标的偏移量（如果提供了 region）
        if region:
            x1, y1, _, _ = region
        else:
            x1, y1 = 0, 0  # 如果没有指定 region，默认为窗口的左上角

        # 遍历识别到的文字坐标，查找目标文字
        for text, (center_x, center_y) in text_coordinates:
            if text == target_text:
                # 将截图坐标转换为全窗口坐标
                global_x = center_x + x1
                global_y = center_y + y1

                # 应用额外的偏移量
                global_x += offset[0]
                global_y += offset[1]

                print(f"找到文字 '{target_text}'，坐标 ({global_x}, {global_y})，偏移 {offset}，点击 {click_times} 次")
                for _ in range(click_times):
                    self.action.click(global_x, global_y)
                return global_x, global_y

        # 如果未找到目标文字
        print(f"未找到目标文字 '{target_text}'")
        return None



