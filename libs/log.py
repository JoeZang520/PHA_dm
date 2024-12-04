import datetime
import os


class Log:
    def __init__(self, logger_name):
        self._logger_name = logger_name
        if str(logger_name).isdigit():
            self._log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../logs/{logger_name}.log")
        else:
            self._log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../{logger_name}.log")

    def current(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _get_colored_msg(self, level, msg, color=None):
        # 默认颜色
        color_codes = {
            "INFO": "\033[92m",    # Green
            "ERROR": "\033[91m",   # Red
            "DEBUG": "\033[94m",   # Blue
            "RESET": "\033[0m"     # Reset color
        }

        # 如果没有传入自定义颜色，则使用默认的颜色
        if color:
            colored_msg = f"{color}{msg}\033[0m"  # 使用自定义颜色
        else:
            # 如果没有自定义颜色，根据级别使用默认颜色
            color = color_codes.get(level, color_codes["RESET"])
            colored_msg = f"{color}[{level}] [{self._logger_name}] {self.current()} {msg}{color_codes['RESET']}"

        return colored_msg

    def info(self, msg, color=None):
        # 如果传入了 color 参数，将使用自定义颜色
        colored_msg = self._get_colored_msg("INFO", msg, color)
        print(colored_msg, flush=True)

        # 写入日志文件
        with open(self._log_file, 'a', encoding='utf-8') as f:
            f.write(f"[INFO] [{self._logger_name}] {self.current()} {msg}\n")

    def error(self, msg):
        colored_msg = self._get_colored_msg("ERROR", msg, None)
        print(colored_msg, flush=True)

        # 写入日志文件
        with open(self._log_file, 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] [{self._logger_name}] {self.current()} {msg}\n")

    def debug(self, msg):
        colored_msg = self._get_colored_msg("DEBUG", msg, None)
        print(colored_msg, flush=True)

    def debug_start(self, msg):
        start_msg = self._get_colored_msg("DEBUG", msg, None)
        print(start_msg, end='', flush=True)

    def debug_append(self, msg='.'):
        print(msg, end='', flush=True)

    def debug_end(self, msg=''):
        print(msg, flush=True)
