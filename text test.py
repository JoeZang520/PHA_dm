from libs.game import Game
from libs.tool import ImageTool, Action, Window
from libs.log import Log
import requests
import base64
import io
import subprocess
import os
import psutil

def launch_ocr():
    project_dir = os.path.abspath(os.path.dirname(__file__))  # 当前脚本所在目录
    ocr_exe_path = os.path.join(project_dir, "OCR", "OCR.exe")  # 项目主目录 + OCR文件夹 + OCR.exe

    # 打印检查路径是否正确
    print("OCR 程序路径：", ocr_exe_path)

    # 确保 OCR.exe 存在
    if not os.path.exists(ocr_exe_path):
        raise FileNotFoundError(f"找不到 OCR 程序文件：{ocr_exe_path}")

    # 检查 OCR 程序是否已在运行
    for proc in psutil.process_iter():
        try:
            # 使用 as_dict() 获取进程信息
            proc_info = proc.as_dict(attrs=['name'])  # 仅获取'name'字段
            if "OCR.exe" == proc_info.get('name', ''):  # 比较名称
                print("OCR 程序已经在运行！")
                return  # 如果程序已经在运行，则不再启动
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # 如果 OCR 程序没有在运行，继续启动
    try:
        subprocess.Popen([ocr_exe_path], cwd=os.path.dirname(ocr_exe_path))  # 启动程序
        print("OCR 程序已打开！")
    except FileNotFoundError:
        print(f"无法找到文件：{ocr_exe_path}")
    except Exception as e:
        print(f"程序运行失败：{e}")

# 测试在某个窗口找到的所有文字
window_id = "007"
# 初始化窗口和动作实例
log = Log(window_id)
window = Window(window_id)
action = Action(window)
image_tool = ImageTool(window, action)
game = Game(window, image_tool, action, log)
launch_ocr()
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






