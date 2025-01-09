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


def timer(seconds, window_id):
    for remaining in range(seconds, -1, -1):
        print(f"\r{window_id} 倒计时: {remaining} 秒", end="")  # 显示倒计时在同一行
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
            game.timer(cycle_time, "等待下一次循环")

        except Exception as e:
            # 捕获异常，防止整个循环被中断
            print(f"窗口 {window_id} 出现异常: {e}，准备重新尝试。")
            continue  # 如果出现异常，跳过当前循环，重新开始




if __name__ == "__main__":
    # 启动 OCR.exe
    launch_ocr()
    # 获取所有账户的 window_id
    accounts = config.get_accounts()
    cycle_time = config.get_cycle_time()

    while True:
        # 每次循环都重新创建进程池
        with multiprocessing.Pool() as pool:
            for window_id in accounts:
                pool.apply_async(pha, (window_id,))
                timer(cycle_time, window_id)
            pool.close()  # 不再接受新任务
            pool.join()  # 等待所有进程完成








