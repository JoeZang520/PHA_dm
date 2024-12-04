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
    action.press("s", second=2)




