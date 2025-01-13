import os
import json

def get_env(key, default=None):
    try:
        # 获取项目根目录路径
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_data_path = os.path.join(root_dir, '.env')
        # 显式指定编码为 'utf-8'
        with open(user_data_path, 'r', encoding='utf-8') as f:
            env = json.load(f)
    except json.JSONDecodeError as e:
        print('ENV JSON格式错误')
        raise e
    except FileNotFoundError:
        env = {}
    return env.get(key, default)

def get_dm_registration():
    registration = get_env('dm_registration', {})
    return registration.get('code'), registration.get('add_code')

def get_accounts():
    accounts = get_env('accounts', {})
    exclude_accounts = get_exclude_accounts()
    # 排除指定的账户，exclude_accounts 是 [1, 2] 形式
    return {window_id: account for index, (window_id, account) in enumerate(accounts.items(), start=1) if index not in exclude_accounts}

def get_cycle_time():
    return get_env('cycle_time', 300)

def get_process_limit():
    return get_env('process_limit', 10)

def get_window_id(window_id):
    return get_accounts().get(window_id)

def get_instance_id(window_id):
    return get_window_id(window_id).get("BlueStacks")

def is_new(window_id):
    return get_window_id(window_id).get("is_new",  False)

def map_code(window_id):
    return get_window_id(window_id).get("map")

def afk(window_id):
    return get_window_id(window_id).get("afk", "稀有")

def dungeon(window_id):
    return get_window_id(window_id).get("dungeon", "None")

def get_exclude_accounts():
    return get_env('exclude_accounts', [])  # 获取排除账户的数字索引
