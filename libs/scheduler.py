import time
import json
import libs.config as config
from libs.task import Task
from datetime import datetime


class Scheduler:
    def __init__(self, window_id, window, image_tool, action, log, interval=3600, last_run=None):
        self.window_id = window_id
        self.window = window
        self.log = log
        self.image_tool = image_tool
        self.action = action
        self.task = Task(window, image_tool, action, log)
        self.is_new = config.is_new(window_id)
        self.pending = self.load_pending("logs/pending.json")
        self.last_run = last_run  # 可设定为默认的时间戳
        self.interval = interval  # 默认1小时（3600秒）
        self.tasks = {
            "task_24": 24 * 60 * 60,  # 24 hours
            "task_12": 12 * 60 * 60,  # 12 hours
            "task_5": 5 * 60 * 60,  # 5 hours
            "task_2": 2 * 60 * 60,  # 2 hours
        }

    def load_pending(self, file_path):
        """加载任务状态"""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_pending(self, file_path, state):
        """保存任务状态，并将时间格式保持为 ISO 8601 字符串"""
        for window_id, tasks in state.items():
            for task_name, task_info in tasks.items():
                timestamp = task_info.get("timestamp")
                if timestamp:
                    if isinstance(timestamp, float):  # 如果是时间戳
                        # 将时间戳转换为 ISO 8601 字符串格式
                        timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
                    # 如果是字符串格式（ISO 8601），不做更改
                    task_info["timestamp"] = timestamp  # 更新任务的时间

        # 保存更新后的任务状态
        with open(file_path, "w") as f:
            json.dump(state, f, indent=4)

    def set_task_status(self, task_name, status):
        """设置任务状态"""
        if self.window_id not in self.pending:
            self.pending[self.window_id] = {}
        task_status = self.pending.get(self.window_id, {})
        task_status[task_name] = {"status": status, "timestamp": time.time()}
        self.pending[self.window_id] = task_status
        self.save_pending("logs/pending.json", self.pending)

    def retry_failed_tasks(self):
        """重新尝试失败的任务"""
        for task_name, task_info in self.pending.get(self.window_id, {}).items():
            if task_info["status"] == "failed":
                print(f"重新尝试任务 {task_name}...")
                self.task.perform(task_name)

    def has_pending_tasks(self):
        """检查是否有待执行的任务"""
        if self.last_run is None:
            return True

        # 如果 last_run 是字符串（ISO 8601 格式），需要转换为时间戳
        if isinstance(self.last_run, str):
            last_run_timestamp = datetime.strptime(self.last_run, '%Y-%m-%dT%H:%M:%S').timestamp()
        else:
            last_run_timestamp = self.last_run  # 如果是时间戳，直接使用

        if time.time() - last_run_timestamp >= self.interval:
            return True
        return False

    def pending_task(self):
        """运行调度任务"""
        print(f"开始调度任务，窗口 ID：{self.window_id}")

        # 检查是否有需要执行的任务
        if not self.has_pending_tasks():
            print("没有待执行的任务，跳过调度任务")
            return  # 跳过调度任务

        # 如果有任务待执行，根据时间间隔执行
        for task_name, interval in self.tasks.items():
            task_info = self.pending.get(self.window_id, {}).get(task_name, {})
            last_run = task_info.get("timestamp", 0)
            status = task_info.get("status", "")

            # 如果 last_run 是字符串（ISO 8601 格式），需要转换为时间戳
            if isinstance(last_run, str):
                last_run = datetime.strptime(last_run, '%Y-%m-%dT%H:%M:%S').timestamp()

            # 检查任务状态和任务是否超出时间间隔
            if status == "failed" or time.time() - last_run >= interval:
                print(f"任务 {task_name} 超过时间间隔或失败，准备执行...")
                try:
                    # 执行任务
                    self.task.perform(task_name)
                    self.task.esc()
                    # 任务执行成功后更新任务状态
                    self.set_task_status(task_name, "completed")
                except Exception as e:
                    # 任务执行失败后更新任务状态
                    print(f"任务 {task_name} 执行失败: {e}")
                    self.set_task_status(task_name, "failed")
            else:
                print(f"任务 {task_name} 没有达到执行条件，状态：{status}")

        # 任务检查和重试失败任务
        self.retry_failed_tasks()
        self.action.click(20, 20)
        self.action.click(20, 20)

