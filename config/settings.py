"""
应用设置模块
从 utils/tools.py 提取的应用配置相关功能
"""
import os
import requests


def get_model_list(model_provider: str, type="text", sub_type="chat"):
    """获取模型列表"""
    base_url = os.getenv(f"{model_provider.upper()}_BASE_URL")
    api_key = os.getenv(f"{model_provider.upper()}_API_KEY")
    
    # 验证环境变量是否设置
    if not base_url:
        return False, f"[ERROR] 未找到环境变量 {model_provider.upper()}_BASE_URL，请检查 .env 配置文件"
    if not api_key and model_provider.upper() != "OLLAMA":
        return False, f"[ERROR] 未找到环境变量 {model_provider.upper()}_API_KEY，请检查 .env 配置文件"
    
    if model_provider.upper() == "OLLAMA":
        url = f"{base_url}/v1/models"
    else:
        url = f"{base_url}/models"
    querystring = {"type": type, "sub_type": sub_type}
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code != 200:
        return False, f"[ERROR] Encounter error {response.status_code} while get model list"
    res = response.json()["data"]
    print(res)
    model_list = []
    for data in res:
        if data["object"] == "model":
            model_list.append(data["id"])
        else:
            pass
    return True, model_list
