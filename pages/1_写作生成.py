"""
写作生成页面
重构自 pages/1_写作生成.py，使用新的模块结构
"""
import streamlit as st
import os
from dotenv import load_dotenv
from warnings import filterwarnings
from config.project_config import get_projects
from core.workflows.novel_workflow import NovelWorkflow
from app.components.input_card import create_input_card
from app.components.model_selector import (
    create_model_selector, 
    create_special_model_selector, 
    create_model_settings
)

filterwarnings("ignore")
load_dotenv()

st.set_page_config(page_title="写作生成", layout="wide")
st.markdown("# 写作生成")
st.sidebar.header("写作生成")

# 初始化session_state中的项目选择
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

# 项目选择和知识库更新
col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom", gap="medium")

with col1:
    # 计算当前项目的索引
    projects = get_projects()
    current_index = None
    if st.session_state.selected_project in projects:
        current_index = projects.index(st.session_state.selected_project)
    
    project = st.selectbox(
        "选择小说项目", 
        options=projects, 
        index=current_index, 
        placeholder="请选择项目", 
        label_visibility="collapsed",
        key="project_selector_writing"
    )
    
    # 更新session_state中的项目选择
    if project != st.session_state.selected_project:
        st.session_state.selected_project = project
with col2:
    refresh_button = st.button("更新知识库", use_container_width=True)
    if refresh_button and project:
        wf = NovelWorkflow(project)
        wf.update()
        st.toast("知识库更新完成")

# 输入区域
col4, col5, col6 = st.columns([1, 1, 1], vertical_alignment="bottom", gap="medium")

with col4:
    user_input = create_input_card(
        "user_input", 
        "用户输入", 
        "请输入生成要求(1000字以内)...", 
        1000, 
        height=355
    )
    outlines_description = create_input_card(
        "outlines_description", 
        "局部大纲描述", 
        "请输入局部大纲描述(5000字以内)...", 
        5000, 
        height=530
    )

with col5:
    temp_settings = create_input_card(
        "temp_settings", 
        "临时设定", 
        "请输入临时设定(10000字以内)，主要输入项目大纲中未提及的临时人物、地点、装备设定等...", 
        10000, 
        height=790
    )
    chapter_num = st.select_slider(
        label="生成的章节数量", 
        options=range(1, int(os.getenv("MAX_GENERATE_NUM", 10)) + 1)
    )
    words_num = st.select_slider(
        label="每章节最低生成字数", 
        options=range(100, int(os.getenv("MAX_CHAPTERS_WORD_NUM", 6000)) + 100, 100)
    )

with col6:
    outlines_generated = create_input_card(
        "outlines_generated", 
        "生成大纲", 
        "生成的大纲会出现在这里...", 
        10000, 
        height=440
    )
    detailed_outlines_generated = create_input_card(
        "detailed_outlines_generated", 
        "生成细纲", 
        "生成的细纲会出现在这里...", 
        20000, 
        height=440
    )

# 进度条
bar = st.progress(0)

# 生成内容区域
col7, col8 = st.columns([1, 2], gap="medium")

with col8:
    novel_generate_area = create_input_card(
        "content_generated", 
        "生成内容", 
        "生成的内容会出现在这里...", 
        100000, 
        height=940
    )

# 模型配置和生成按钮
with col7:
    model_provider_selection, model_selection = create_model_selector()
    special_model_provider_selection, extractor_model_selection, short_model_selection = create_special_model_selector()
    model_kwargs = create_model_settings()

    def outlines_generate():
        """生成大纲"""
        try:
            if not project:
                st.toast("请先选择项目")
                return
            if not model_provider_selection:
                st.toast("请先选择模型服务商")
                return
            if not model_selection:
                st.toast("请先选择模型")
                return
            
            wf = NovelWorkflow(
                project, 
                model_selection, 
                model_provider_selection, 
                extractor_model_selection, 
                short_model_selection, 
                special_model_provider_selection, 
                model_kwargs
            )
            inputs = {
                "user_input": st.session_state.get("user_input_text"),
                "temp_settings": st.session_state.get("temp_settings_text"),
                "chapter_num": chapter_num,
                "words_num": words_num,
                "outlines_description": st.session_state.get("outlines_description_text")
            }
            outline_str, outline_list = wf.generate_outlines(inputs, lambda p: bar.progress(p))
            st.session_state["outlines_generated_text"] = outline_str
            st.session_state["outline_list"] = outline_list
            bar.progress(100)
            st.toast("生成完成")
        except Exception as e:
            st.error(f"生成大纲时发生错误: {e}")
            import traceback
            st.error(traceback.format_exc())

    def detailed_outlines_generate():
        """生成细纲"""
        try:
            if not project:
                st.toast("请先选择项目")
                return
            if not model_provider_selection:
                st.toast("请先选择模型服务商")
                return
            if not model_selection:
                st.toast("请先选择模型")
                return
            if not st.session_state.get("outline_list"):
                st.toast("请先生成章节大纲")
                return
            
            wf = NovelWorkflow(
                project, 
                model_selection, 
                model_provider_selection, 
                extractor_model_selection, 
                short_model_selection, 
                special_model_provider_selection, 
                model_kwargs
            )
            inputs = {
                "user_input": st.session_state.get("user_input_text"),
                "temp_settings": st.session_state.get("temp_settings_text"),
                "chapter_num": chapter_num,
                "words_num": words_num,
                "outlines_description": st.session_state.get("outlines_description_text"),
                "chapter_outlines": st.session_state.get("outline_list")
            }
            detailed_outline_str, detailed_outline_list = wf.generate_detailed_outlines(inputs, lambda p: bar.progress(p))
            st.session_state["detailed_outlines_generated_text"] = detailed_outline_str
            st.session_state["detailed_outline_list"] = detailed_outline_list
            bar.progress(100)
            st.toast("细纲生成完成")
        except Exception as e:
            st.error(f"生成细纲时发生错误: {e}")
            import traceback
            st.error(traceback.format_exc())

    def novel_generate():
        """生成小说"""
        try:
            if not project:
                st.toast("请先选择项目")
                return
            if not model_provider_selection:
                st.toast("请先选择模型服务商")
                return
            if not model_selection:
                st.toast("请先选择模型")
                return
            
            wf = NovelWorkflow(
                project, 
                model_selection, 
                model_provider_selection, 
                extractor_model_selection, 
                short_model_selection, 
                special_model_provider_selection, 
                model_kwargs
            )
            if st.session_state.get("outlines_generated_text"):
                inputs = {
                    "user_input": st.session_state.get("user_input_text"),
                    "temp_settings": st.session_state.get("temp_settings_text"),
                    "chapter_num": chapter_num,
                    "words_num": words_num,
                    "generated_outlines": st.session_state.get("outline_list") if st.session_state.get("outline_list") else st.session_state.get("outlines_generated_text", "").split("\\n\\n"),
                    "outlines_description": st.session_state.get("outlines_description_text")
                }
                
                # 创建状态显示区域
                status_placeholder = st.empty()
                
                for i, content in enumerate(wf.generate_novels(
                    inputs, 
                    lambda p: bar.progress(p),
                    lambda s: status_placeholder.info(s)
                )):
                    if content:
                        current_text = st.session_state.get("content_generated_text", "")
                        st.session_state["content_generated_text"] = current_text + f"## 章节{i+1}\n" + str(content) + "\n\n"
                
                status_placeholder.success("🎉 全部章节生成完成！")
                bar.progress(100)
                st.toast("生成完成")
            else:
                st.toast("请生成或输入大纲内容")
        except Exception as e:
            st.error(f"生成小说时发生错误: {e}")
            import traceback
            st.error(traceback.format_exc())

    outlines_gen_button = st.button(
        "自动生成大纲", 
        use_container_width=True, 
        type="primary", 
        on_click=outlines_generate
    )
    detailed_outlines_gen_button = st.button(
        "生成细纲", 
        use_container_width=True, 
        type="primary", 
        on_click=detailed_outlines_generate
    )
    chapters_gen_button = st.button(
        "自动生成章节", 
        use_container_width=True, 
        type="primary", 
        on_click=novel_generate
    )
    save_button = st.button("保存", use_container_width=True, type="primary")

    @st.dialog("保存内容")
    def save():
        """保存生成的内容"""
        file_name = st.text_input(
            "文件名", 
            placeholder="请输入文件名，文档将会保存到项目上下文目录", 
            label_visibility="collapsed"
        )
        col_save, col_cancel = st.columns(2, gap="small")
        wf = NovelWorkflow(project)
        with col_save:
            if st.button("保存", type="primary", use_container_width=True):
                with open(f"{wf.context_retriever.document_processor.documents_dir}/{file_name}.txt", "w", encoding="utf-8") as f:
                    data = "## 大纲\n" + st.session_state.get("outlines_generated_text", "") + "\n\n"
                    if st.session_state.get("detailed_outlines_generated_text"):
                        data += "## 细纲\n" + st.session_state.get("detailed_outlines_generated_text", "") + "\n\n"
                    data += "## 内容\n" + st.session_state.get("content_generated_text", "")
                    f.write(data)
                st.rerun()
        with col_cancel:
            if st.button("取消", use_container_width=True):
                st.rerun()
                
    if save_button:
        if project:
            save()
        else:
            st.toast("请先选择项目")