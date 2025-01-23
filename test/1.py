import time

from libs.game import Game
from libs.tool import ImageTool, Action, Window
from libs.log import Log
import requests
import base64
import io
import subprocess
import os
import psutil


# 测试在某个窗口找到的所有文字
window_id = "002"
# 初始化窗口和动作实例
log = Log(window_id)
window = Window(window_id)
action = Action(window)
image_tool = ImageTool(window, action)
game = Game(window, image_tool, action, log)
# window.launch_ocr()
# 打开窗口
window.open_window()


# 调用示例
all_equips = game.book_orange(2)
if all_equips:
    game.esc(2)
    action.click(540, 331, pos="左箭头")
    action.click(402, 144, pos="装备升级")
    action.click(294, 633, pos="大装备升级")

    base_x = 118
    base_y = 689
    offset = 70  # 每次点击水平偏移量
    row_offset = 70

    for row in range(2):  # 控制行数，范围为 0 和 1，表示两行
        for i in range(6):  # 每行点击 6 次
            action.click(base_x + i * offset, base_y + row * row_offset)
            equips = image_tool.read_text((230, 342, 418, 371))
            print(f'equips{equips}')
            print(f'all_equips{all_equips}')
            if equips in all_equips:
                game.upgrade_eqip()
            else:
                print("装备不匹配")

game.esc(2)
image_tool.picture("right")










