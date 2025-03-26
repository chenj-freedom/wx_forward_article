import yaml

# 加载配置文件
def load_config(config_file='config.yaml'):
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: 配置文件 {config_file} 未找到")
        return {}
    except yaml.YAMLError as e:
        print(f"Error: 解析配置文件时出错 -> {e}")
        return {}

# 获取腾讯的 app_id 和 app_key
def get_tencent_config(config_file='config.yaml'):
    config = load_config(config_file)
    tencent_config = config.get('tencent', {})
    app_id = tencent_config.get('app_id')
    app_key = tencent_config.get('app_key')
    return app_id, app_key
