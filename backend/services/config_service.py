import os
import ast

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'base_config.py')

def get_config():
    config = {}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        code = f.read()
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0].id
            if name in [
                'PLATFORM', 'KEYWORDS', 'LOGIN_TYPE', 'COOKIES', 'SORT_TYPE', 'PUBLISH_TIME_TYPE',
                'CRAWLER_TYPE', 'WEIBO_SEARCH_TYPE', 'UA', 'ENABLE_IP_PROXY', 'CRAWLER_MAX_SLEEP_SEC',
                'IP_PROXY_POOL_COUNT', 'IP_PROXY_PROVIDER_NAME', 'HEADLESS', 'SAVE_LOGIN_STATE',
                'ENABLE_CDP_MODE', 'CDP_DEBUG_PORT', 'CUSTOM_BROWSER_PATH', 'CDP_HEADLESS',
                'BROWSER_LAUNCH_TIMEOUT', 'AUTO_CLOSE_BROWSER', 'SAVE_DATA_OPTION', 'USER_DATA_DIR',
                'START_PAGE', 'CRAWLER_MAX_NOTES_COUNT', 'MAX_CONCURRENCY_NUM', 'ENABLE_GET_IMAGES',
                'ENABLE_GET_COMMENTS', 'CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES', 'ENABLE_GET_SUB_COMMENTS',
            ]:
                try:
                    config[name.lower()] = ast.literal_eval(node.value)
                except Exception:
                    pass
    return config

def save_config(data):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        for k, v in data.items():
            key = k.upper()
            if line.strip().startswith(f'{key} ='):
                if isinstance(v, str):
                    v_str = f'"{v}"'
                else:
                    v_str = str(v)
                lines[i] = f'{key} = {v_str}\n'
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return {"status": "saved"} 