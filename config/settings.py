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
    print(base_url, api_key)
    
    # 验证环境变量是否设置
    if not base_url:
        return False, f"[ERROR] 未找到环境变量 {model_provider.upper()}_BASE_URL，请检查 .env 配置文件"
    if not api_key and model_provider.upper() != "OLLAMA":
        return False, f"[ERROR] 未找到环境变量 {model_provider.upper()}_API_KEY，请检查 .env 配置文件"
    
    if model_provider.upper() == "OLLAMA":
        url = f"{base_url.rstrip('/')}/v1/models"
    else:
        url = f"{base_url.rstrip('/')}/models"
    # querystring = {"type": type, "sub_type": sub_type}
    headers = {"Authorization": f"Bearer {api_key}"}
    # reponse = requests.get(url, headers=headers, params=querystring)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return False, f"[ERROR] Encounter error {response.status_code} while get model list"
    try:
        json_data = response.json()
        if "data" in json_data:
             res = json_data["data"]
        else:
             # 有些 API 可能直接返回列表，或者结构不同
             res = json_data
             
        print(f"Model List Response: {res}")
        
        if not isinstance(res, list):
             return False, f"[ERROR] Unexpected response format: {res}"

        model_list = []
        for data in res:
            if isinstance(data, dict) and "id" in data:
                 model_list.append(data["id"])
            elif isinstance(data, str):
                 model_list.append(data)
        return True, model_list
    except Exception as e:
         return False, f"[ERROR] Failed to parse response: {e}"
