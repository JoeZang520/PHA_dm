import random
import time

from libs.game import Game
from libs.tool import ImageTool, Action, Window
from libs.log import Log


for window_id in ["001"]:
    # 初始化窗口和动作实例
    log = Log(window_id)
    window = Window(window_id)
    action = Action(window)
    image_tool = ImageTool(action)
    game = Game(image_tool, action, log, window_id)

    # 打开窗口
    window.open_window()

def party_boss():
    game.switch("auto_green.png")
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
    found_que_green = False  # 是否找到 que_green.png

    for _ in range(50):
        # 如果找到 que_green.png
        if image_tool.image("que_green.png"):
            if not found_que_green:  # 如果第一次找到
                found_que_green = True  # 设置已找到
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
            steps = random.uniform(5, 6)

        # 执行按键（支持单方向和双方向）
        action.press(*direction, second=steps)

        # 更新上一次的方向
        last_direction = direction

        # 如果已执行了 5 轮额外操作且图片已找到，退出循环
        if extra_rounds == 0 and found_que_green:
            break


party_boss()
