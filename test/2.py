import subprocess
import os
import time
def launch_ocr():
    project_dir = os.path.abspath(os.path.dirname(__file__))  # 当前脚本所在目录
    ocr_exe_path = os.path.join(project_dir, "OCR", "OCR.exe")  # 项目主目录 + OCR文件夹 + OCR.exe

    # 打印检查路径是否正确
    print("OCR 程序路径：", ocr_exe_path)

    # 确保 OCR.exe 存在
    if not os.path.exists(ocr_exe_path):
        raise FileNotFoundError(f"找不到 OCR 程序文件：{ocr_exe_path}")

    # 直接打开 OCR.exe
    try:
        subprocess.Popen([ocr_exe_path], cwd=os.path.dirname(ocr_exe_path))  # 打开程序
        print("OCR 程序已打开！")
        time.sleep(5)
    except FileNotFoundError:
        print(f"无法找到文件：{ocr_exe_path}")
    except Exception as e:
        print(f"程序运行失败：{e}")


