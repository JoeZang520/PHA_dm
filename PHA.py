import libs.config as config
from libs.log import Log
from libs.game import Game
from libs.new import New
from libs.tool import ImageTool, Action, Window
from libs.scheduler import Scheduler
import multiprocessing
import time
import subprocess
import os
import psutil

cycle_time = config.get_cycle_time()
def timer(seconds, activity_name, window_id):
    for remaining in range(seconds, -1, -1):
        print(f"\r{window_id} {activity_name}: {remaining} 秒", end="")  # 显示倒计时在同一行
        time.sleep(1)  # 等待 1 秒
    print(f"\n")  # 换行并打印结束信息

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

def pha(window_id):
    while True:
        try:
            window = Window(window_id)
            log = Log(window_id)
            action = Action(window)
            image_tool = ImageTool(window, action)
            game = Game(window, image_tool, action, log)
            new = New(window, image_tool, action, game, log)
            scheduler = Scheduler(window_id, window, image_tool, action, game, log)

            # 尝试进入游戏，失败则重新尝试
            if not game.enter_game():
                print(f"窗口 {window_id} 进入游戏失败，准备重新尝试。")
                continue  # 跳过当前循环，重新开始

            game.handle_dialog()
            game.choose_map()
            game.collect_diamond()

            # 如果是新任务，执行新手引导任务
            if config.is_new(window_id):
                new.task_guide()

            # 执行每日任务
            scheduler.pending_task(window_id)
            action.click(40, 275)  # 点击自动休眠
            game.switch_rarity(window_id)

            timer(cycle_time, "等待下一次循环", window_id)
        except Exception as e:
            return


# 用于存储窗口对应的进程
window_processes = {}

if __name__ == "__main__":
    # 启动 OCR.exe
    launch_ocr()
    # 获取所有账户的 window_id
    accounts = config.get_accounts()

    while True:
        for window_id in accounts:
            if window_id not in window_processes or not window_processes[window_id].is_alive():
                # 如果该窗口没有进程或者进程已经结束，创建新的进程
                p = multiprocessing.Process(target=pha, args=(window_id,))
                window_processes[window_id] = p
                p.start()  # 启动新的进程
                print(f"创建新的进程来处理窗口 {window_id}")
            else:
                print(f"窗口 {window_id} 已在运行，跳过重新创建进程。")
            time.sleep(100)









