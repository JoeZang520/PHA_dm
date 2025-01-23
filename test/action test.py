from libs.log import Log
import libs.config as config
from libs.game import Game
from libs.task import Task
from libs.new import New
from libs.tool import ImageTool, Action, Window
from libs.scheduler import Scheduler

window_id = "002"
window = Window(window_id)
log = Log(window_id)
action = Action(window)
image_tool = ImageTool(window, action)
game = Game(window, image_tool, action, log)
task = Task(window, window_id, image_tool, action, game, log)
new = New(window, image_tool, action, game, log)
scheduler = Scheduler(window_id, window, image_tool, action, game, log)
window.launch_ocr()
game.enter_game()



# 以下是测试代码
action.click(540,331, activity="左箭头")
