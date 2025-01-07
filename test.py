import subprocess
import os
import time
import socket


def launch_ocr_and_server(ocr_dir="OCR", port=20086):
    """
    启动 OCR.exe 和服务器
    """
    # 获取当前项目主目录
    project_dir = os.path.abspath(os.path.dirname(__file__))  # 当前脚本所在目录
    ocr_exe_path = os.path.join(project_dir, ocr_dir, "OCR.exe")  # OCR.exe 的完整路径

    # 检查 OCR.exe 是否存在
    if not os.path.exists(ocr_exe_path):
        raise FileNotFoundError(f"找不到 OCR 程序文件：{ocr_exe_path}")

    # 启动 OCR.exe
    try:
        print(f"OCR 程序路径：{ocr_exe_path}")
        subprocess.Popen([ocr_exe_path], cwd=os.path.dirname(ocr_exe_path))  # 打开 OCR.exe
        print("OCR 程序已打开！")
        time.sleep(5)  # 等待 OCR.exe 初始化
    except Exception as e:
        print(f"启动 OCR 程序失败：{e}")
        return

    # 检查端口是否被占用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('0.0.0.0', port)) == 0:
            print(f"端口 {port} 已被占用，请释放端口或选择其他端口。")
            return

    # 启动服务器
    try:
        print(f"即将启动服务器，监听端口 {port}...")
        import uvicorn
        uvicorn.run("app:app", host="0.0.0.0", port=port)
    except Exception as e:
        print(f"启动服务器失败：{e}")


if __name__ == "__main__":
    launch_ocr_and_server()
