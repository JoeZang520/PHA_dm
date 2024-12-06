from libs.game import Game
from libs.tool import ImageTool, Action, Window
from libs.log import Log
import requests
import base64
import io


for window_id in ["001"]:
    # 初始化窗口和动作实例
    log = Log(window_id)
    window = Window(window_id)
    action = Action(window)
    image_tool = ImageTool(action)
    game = Game(image_tool, action, log, window_id)

    # 打开窗口
    window.open_window()

    screenshot = action.window.capture_window()
    if screenshot is None:
        print("无法获取截图")

    # 将图片转换为 base64 编码
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # 向服务器发送 POST 请求进行 OCR 识别
    url = "http://127.0.0.1:20086/base64"
    res = requests.post(url, json={"img": img_base64})

    # 获取返回的 JSON 数据
    response_data = res.json()

    # 提取识别到的文字和坐标信息
    if response_data["code"] == 1 and response_data["data"]:
        for item in response_data["data"]:
            print(item["text"])
    else:
        print("未识别到任何文字。")







