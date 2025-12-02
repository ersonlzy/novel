import streamlit as st
import os
from utils.tools import (
    get_projects,
    get_model_list,
)
import time
from dotenv import load_dotenv
from datetime import datetime
from workflows.novel_wf import Novel
from warnings import filterwarnings

filterwarnings("ignore")

load_dotenv()

def fullscreen_input_modal(key, placeholder, max_chars, current_value=""):
    @st.dialog("全屏编辑", width="large")
    def modal():
        content = st.text_area(
            label="输入框",
            value=current_value,
            max_chars=max_chars,
            height=800,
            key=f"{key}_modal",
            label_visibility="collapsed",
            placeholder=placeholder,
        )
        
        # 操作按钮
        col1, col2, col3 = st.columns([1, 1, 2], gap="small")
        
        with col1:
            if st.button("保存", use_container_width=True, key=f"save_{key}"):
                st.session_state[f"{key}_text"] = content
                st.rerun()
        with col2:
            if st.button("放弃", use_container_width=True, key=f"cancel_{key}"):
                if f"{key}_modal" in st.session_state:
                    del st.session_state[f"{key}_modal"]
                st.rerun()
    return modal


def create_input_card(key, label, placeholder, max_chars, height=150):
    if f"{key}_text" not in st.session_state:
        st.session_state[f"{key}_text"] = ""
    
    col_title, col_expand = st.columns([15, 5], vertical_alignment="top", gap="small")
    
    with col_title:
        st.markdown(f'**{label}**', unsafe_allow_html=False)
    
    with col_expand:
        if st.button("全屏编辑", key=f"expand_{key}", help="全屏编辑", use_container_width=True, type="tertiary"):
            current_value = st.session_state.get(f"{key}_text", "")
            modal_func = fullscreen_input_modal(key, placeholder, max_chars, current_value)
            modal_func()

    value = st.text_area(
        label="输入框",
        placeholder=placeholder,
        max_chars=max_chars,
        height=height,
        value=st.session_state.get(f"{key}_text", ""),
        key=f"{key}_text",
        label_visibility="collapsed"
    )
    
    if value != st.session_state.get(f"{key}_text", ""):
        st.session_state[f"{key}_text"] = value

    
    
    return st.session_state.get(f"{key}_text", "")


st.set_page_config(page_title="写作生成", layout="wide")
st.markdown("# 写作生成")
st.sidebar.header("写作生成")

col1, col2, col3= st.columns([1,1,1], vertical_alignment="bottom", gap="medium")

with col1:
    project = st.selectbox("选择小说项目", options=get_projects(), index=None, placeholder="请选择项目", label_visibility="collapsed")
with col2:
    refresh_button = st.button("更新知识库", width="stretch")

col4, col5, col6 = st.columns([1,1,1], vertical_alignment="bottom",  gap="medium")

            
with col4:
    user_input = create_input_card("user_input", "用户输入", "请输入生成要求(1000字以内)...", 1000, height=355)
    outlines_description = create_input_card("outlines_description", "局部大纲描述", "请输入局部大纲描述(5000字以内)...", 5000, height=530)

with col5:
    temp_settings = create_input_card("temp_settings", "临时设定", "请输入临时设定(10000字以内)，主要输入项目大纲中未提及的临时人物、地点、装备设定等...", 10000, height=790)
    chapter_num = st.select_slider(label="生成的章节数量", options=range(1,int(os.getenv("MAX_GENERATE_NUM", 10)) + 1))
    words_num = st.select_slider(label="每章节生成字数", options=range(100, int(os.getenv("MAX_CHAPTERS_WORD_NUM", 6000)) + 100, 100))
with col6:
    outlines_generated = create_input_card("outlines_generated", "生成大纲", "生成的大纲会出现在这里...", 10000, height=940)
    col61, col62 = st.columns(2, gap="small")



bar = st.progress(0)

col7, col8 = st.columns([1,2], gap="medium")



with col8:
    novel_generate_area = create_input_card("content_generated", "生成内容", "生成的内容会出现在这里...", 100000, height=940)
   
        

with col7:
    def __get_model_list(model_provider):
        if model_provider is None:
            return ["请先选择模型服务商"]
        else:   
            res, model_list = get_model_list(model_provider)
            if res:
                return model_list
            else:
                st.toast(f"获取模型列表失败, 请检查配置文件\n{model_list}")
                return []
    model_provider_selection = st.selectbox("模型配置", options=["siliconflow", "deepseek", "dashscope", "openai", "ollama"], index=None, placeholder="请选择生成模型服务商", label_visibility="collapsed")
    model_selection = st.selectbox("模型配置", options=__get_model_list(model_provider_selection), index=None, placeholder="请选择生成模型", label_visibility="collapsed")
    special_model_selection = st.expander("特殊模型配置", expanded=False)
    with special_model_selection:
        special_model_provider_selection = st.selectbox("特殊模型服务商", options=["siliconflow", "dashscope", "ollama"], index=0, placeholder="请选择模型服务商", label_visibility="collapsed")
        options = __get_model_list(special_model_provider_selection)
        index = options.index("Qwen/Qwen3-8B") if "Qwen/Qwen3-8B" in options else 0
        extractor_model_selection = st.selectbox("检索提取模型", options=options, index=index, placeholder="请选择提取器模型")
        short_model_selection = st.selectbox("内容缩写模型", options=options, index=index, placeholder="请选择缩写器模型")
    model_settings = st.expander("生成模型配置", expanded=True) 
    with model_settings:
        temperature = st.slider("温度", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
        top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
        frequency_penalty = st.slider("重复生成惩罚", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
        presence_penalty = st.slider("已生成惩罚", min_value=0.0, max_value=2.0, value=0.0, step=0.1)


    def outlines_generate():
        if not project:
            st.toast("请先选择项目")
            return
        if not model_provider_selection:
            st.toast("请先选择模型服务商")
            return
        if not model_selection:
            st.toast("请先选择模型")
            return
        
        model_kwargs = {
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        wf = Novel(project, model_selection, model_provider_selection, extractor_model_selection, short_model_selection, special_model_provider_selection, model_kwargs)
        inputs = {
            "user_input": st.session_state.get("user_input_text"),
            "temp_settings": st.session_state.get("temp_settings_text"),
            "chapter_num": chapter_num,
            "words_num": words_num,
            "outlines_description": st.session_state.get("outlines_description_text")
        }
        outline_str, outline_list =  wf.generate_outlines(inputs, bar)
        st.session_state["outlines_generated_text"] = outline_str
        st.session_state["outline_list"] = outline_list
        bar.progress(100)
        st.toast("生成完成")

    def novel_generate():
        if not project:
            st.toast("请先选择项目")
            return
        if not model_provider_selection:
            st.toast("请先选择模型服务商")
            return
        if not model_selection:
            st.toast("请先选择模型")
            return
        model_kwargs = {
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        wf = Novel(project, model_selection, model_provider_selection, extractor_model_selection, short_model_selection, special_model_provider_selection, model_kwargs)
        if st.session_state.get("outlines_generated_text"):
            inputs = {
                "user_input": st.session_state.get("user_input_text"),
                "temp_settings": st.session_state.get("temp_settings_text"),
                "chapter_num": chapter_num,
                "words_num": words_num,
                "generated_outlines": st.session_state.get("outline_list") if st.session_state.get("outline_list") else st.session_state.get("outlines_generated_text", "").split("\n\n"),
                "outlines_description": st.session_state.get("outlines_description_text")
            }
            for content in wf.generate_novels(inputs, bar):
                if content:
                    current_text = st.session_state.get("content_generated_text", "")
                    st.session_state["content_generated_text"] = current_text + str(content) + "\n\n"
            bar.progress(100)
            st.toast("生成完成")
        else:
            st.toast("请生成或输入大纲内容")



    outlines_gen_button = st.button("自动生成大纲", width="stretch", type="primary", on_click=outlines_generate)
    chapters_gen_button = st.button("自动生成章节", width="stretch", type="primary", on_click=novel_generate)
    save_button = st.button("保存", width="stretch", type="primary")

    





    @st.dialog("保存内容")
    def save():
        file_name = st.text_input("文件名", placeholder="请输入文件名，文档将会保存到项目上下文目录", label_visibility="collapsed")
        col_save, col_cancel = st.columns(2, gap="small")
        wf = Novel(project)
        with col_save:
            if st.button("保存", type="primary", width="stretch"):
                with open(f"{wf.context_retriever.document_processor.documents_dir}/{file_name}.txt", "w", encoding="utf-8") as f:
                    f.write(st.session_state["content_generated_text"])
                st.rerun()
        with col_cancel:
            if st.button("取消", width="stretch"):
                st.rerun()
                
    if save_button:
        if project:
            save()
        else:
            st.toast("请先选择项目")