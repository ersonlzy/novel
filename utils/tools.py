import os
import yaml
from argparse import Namespace
import streamlit as st
import yaml
import shutil
import requests



def get_config(project, path=None):
    if not path:
        config_path = os.path.join("./projects", f"{project}.yaml")
    else:
        config_path = os.path.join(path, f"{project}.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        args = yaml.load(f, Loader=yaml.FullLoader)
    return Namespace(**args)


def get_projects(path=None):
    if not path:
        path = "./projects"
    configs = [config.replace(".yaml", "") for config in os.listdir(path)]
    return configs

    
def get_documents_info(path):
    files = os.listdir(path)
    data = {"文件": files}
    sizes = []
    for file in files:
        size = os.path.getsize(os.path.join(path, file)) / 1024 / 1024 # MB
        sizes.append(f"{size:.2f} MB")
    data.update({"文件大小": sizes})
    return data


def create_new_project(project, pd="", cd="", kd=""):
    if pd == "":
        pd = f"./knowledgebase/{project}/project_documents"
    if cd == "":
        cd = f"./knowledgebase/{project}/context_documents"
    if kd == "":
        kd = f"./knowledgebase/{project}/knowledge_documents"

    try:
        os.mkdir(f"./knowledgebase/{project}")
    except FileExistsError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create path ./knowledgebase/{project}")
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
        with open(f"./projects/{project}.yaml", "w", encoding="utf-8") as f:
            data = {
                    "project_documents": pd,
                    "context_documents": cd,
                    "knowledge_documents": kd
                }
            yaml.dump(data, f, allow_unicode=True)
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while create file ./projects/{project}.yaml")
        return False
    return True


def delete_project(project):
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
        shutil.rmtree(f"./knowledgebase/{project}", ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete dirs ./knowledgebase/{project}")
        return False
    
    try:
        shutil.rmtree(f"./.vectordb/{project}", ignore_errors=True)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete persistent storage ./.vectordb/{project}")
        return False

    try:
        os.remove(f"./projects/{project}.yaml")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete file ./projects/{project}.yaml")
        return False

    try:
        os.remove(f"./.db/{project}_record_manager_cache.db")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[ERROR] Encounter error {e} while delete file ./projects/{project}.yaml")
        return False
    return True


@st.dialog("请确认操作")
def confirm(opearation, confirm_word, callback_fn):
    st.write(f"请确认操作:{opearation}，且操作不可逆")
    col311, col312 = st.columns([3,1], gap="small", vertical_alignment="bottom")
    with col311:
        res = st.text_input(label="请确认输入", placeholder=confirm_word, label_visibility="hidden")
    with col312:
        submit = st.button("确认")
    if submit:
        if res == confirm_word:
            st.rerun()
            if callback_fn(confirm_word):
                st.warning(f"操作：{opearation}执行完成")
            else:
                st.error(f"操作：{opearation}执行失败")
        else:
            st.error('输入错误')


def get_model_list(model_provider:str):
    base_url = os.getenv(f"{model_provider.upper()}_BASE_URL")
    api_key = os.getenv(f"{model_provider.upper()}_API_KEY")
    url = f"{base_url}/models"
    querystring = {"type":"text","sub_type":"chat"}
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code != 200:
        return False, f"[ERROR] Encounter error {response.status_code} while get model list"
    res = response.json()["data"]
    model_list = []
    for data in res:
        if data["object"] == "model":
            model_list.append(data["id"])
        else:
            pass
    return True, model_list