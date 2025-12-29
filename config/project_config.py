"""
项目配置管理模块
从 utils/tools.py 提取的项目配置相关功能
"""
import os
import yaml
from argparse import Namespace
import shutil


def get_config(project, path=None):
    """获取项目配置"""
    if not path:
        config_path = os.path.join("data/projects", f"{project}.yaml")
    else:
        config_path = os.path.join(path, f"{project}.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        args = yaml.load(f, Loader=yaml.FullLoader)
    return Namespace(**args)


def get_projects(path=None):
    """获取所有项目列表"""
    if not path:
        path = "data/projects"
    configs = [config.replace(".yaml", "") for config in os.listdir(path)]
    return configs


def create_new_project(project, pd="", cd="", kd=""):
    """创建新项目"""
    if pd == "":
        pd = f"data/knowledgebase/{project}/project_documents"
    if cd == "":
        cd = f"data/knowledgebase/{project}/context_documents"
    if kd == "":
        kd = f"data/knowledgebase/{project}/knowledge_documents"

    try:
        os.mkdir(f"data/knowledgebase/{project}")
    except FileExistsError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create path data/knowledgebase/{project}")
        return False
    
    try:
        os.mkdir(pd)
    except FileExistsError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create path {pd}")
        return False
    
    try:
        os.mkdir(cd)
    except FileExistsError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create path {cd}")
        return False
    
    try:
        os.mkdir(kd)
    except FileExistsError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create path {kd}")
        return False
    
    try:
        with open(f"data/projects/{project}.yaml", "w", encoding="utf-8") as f:
            data = {
                    "project_documents": pd,
                    "context_documents": cd,
                    "knowledge_documents": kd
                }
            yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create file data/projects/{project}.yaml")
        return False
    return True


def delete_project(project):
    """删除项目"""
    config = get_config(project)
    try:
        shutil.rmtree(config.project_documents, ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete dirs {config.project_documents}")
        return False
    
    try:
        shutil.rmtree(config.context_documents, ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete dirs {config.context_documents}")
        return False

    try:
        shutil.rmtree(config.knowledge_documents, ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete dirs {config.knowledge_documents}")
        return False
    
    try:
        shutil.rmtree(f"data/knowledgebase/{project}", ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete dirs data/knowledgebase/{project}")
        return False
    
    try:
        shutil.rmtree(f".vectordb/{project}", ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete persistent storage .vectordb/{project}")
        return False

    try:
        os.remove(f"data/projects/{project}.yaml")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete file data/projects/{project}.yaml")
        return False

    try:
        os.remove(f".db/{project}_record_manager_cache.db")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete file .db/{project}_record_manager_cache.db")
        return False
    return True
