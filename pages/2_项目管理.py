import streamlit as st
import os
import subprocess
import platform
from utils.tools import (
    get_projects,
    get_config,
    create_new_project,
    delete_project,
)
from workflows.novel_wf import Novel

def open_folder(folder_path):
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", folder_path])
        elif platform.system() == "Windows":
            subprocess.Popen(f'explorer "{folder_path}"')
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", folder_path])
    except Exception as e:
        st.error(f"打开文件夹失败: {e}")


def delete_file(filepath):
    try:
        os.remove(filepath)
        st.toast(f"删除文件成功")
    except Exception as e:
        st.toast(f"删除文件失败: {e}")


def display_file_list_with_delete(folder_path, tab_name):
    try:
        files = os.listdir(folder_path)
        if not files:
            st.info("暂无文件")
            return
        
        # 创建表格数据
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                col1, col2, col3 = st.columns([3, 1, 1], vertical_alignment="center", gap="small")
                
                with col1:
                    size = os.path.getsize(file_path) / 1024 / 1024  # MB
                    st.write(f"📄 {file} ({size:.2f} MB)")
                
                with col2:  
                    st.text("")  # 占位
                
                with col3:
                    if st.button("🗑️ 删除", key=f"delete_{tab_name}_{file}", use_container_width=True):
                        @st.dialog("删除确认", width="small")
                        def confirm_delete():
                            st.write(f"确认删除文件: **{file}** ?")
                            col_confirm, col_cancel = st.columns(2, gap="small")
                            
                            with col_confirm:
                                delete = st.button("确认删除", use_container_width=True)
                                if delete:
                                    delete_file(file_path)
                                    st.rerun()

                            with col_cancel:
                                if st.button("取消", use_container_width=True):
                                    st.rerun()

                        confirm_delete()
    except FileNotFoundError:
        st.error("未找到知识库文件夹，请检查项目配置文件")


st.set_page_config(page_title="项目管理", page_icon="✏️", layout="wide")
st.markdown("# 项目管理")
st.sidebar.header("项目管理")



col1, col2, col3= st.columns([1,1,1], vertical_alignment="bottom", gap="medium")


with col1:
    project = st.selectbox("选择小说项目", options=get_projects(), index=None, placeholder="请选择项目", accept_new_options=True, label_visibility="collapsed")
with col2:
    refresh_button = st.button("更新项目", width="stretch")
    if refresh_button:
        wf = Novel(project)
        wf.update()
with col3:
    delete_button = st.button("删除项目", width="stretch")
    if delete_button:
        @st.dialog("请确认操作")
        def confirm(opearation, confirm_word):
            st.write(f"请确认操作:{opearation}，且操作不可逆")
            col311, col312 = st.columns([3,1], gap="small", vertical_alignment="bottom")
            with col311:
                res = st.text_input(label="请确认输入", placeholder=confirm_word, label_visibility="collapsed")
            with col312:
                submit = st.button("确认")
            if submit:
                if res == confirm_word:
                    if delete_project(project):
                        st.toast(f"项目{project}删除完成", duration=5)
                    else:
                        st.toast(f"项目{project}删除失败", duration=5)
                    st.rerun()
                else:
                    st.error('输入错误')
        confirm(f'删除{project}', project)
        
if project not in get_projects() and project is not None:   
    project_documents_path = st.text_input(label='请输入项目知识库文件路径, 留空为默认路径')
    context_documents_path = st.text_input(label='请输入上下文知识库文件路径, 留空为默认路径')
    knowledge__documents_path = st.text_input(label='请输入背景知识库文件路径, 留空为默认路径')
    create_project = st.button("新建项目")
    if create_project:
        if create_new_project(project, project_documents_path, context_documents_path, knowledge__documents_path):
            st.toast(f"项目{project}创建成功", duration=5)
        else:
            st.toast(f"项目{project}创建失败", duration=5)
elif project:
    tab1, tab2, tab3 = st.tabs(["项目知识库", "上下文知识库", "背景知识库"])
    with tab1:
        project_documents = st.expander(f"项目: {project} - 项目知识库", expanded=True)
        with project_documents:
            col_header1, col_header2 = st.columns([1, 1], vertical_alignment="center", gap="small")
            with col_header1:
                st.subheader("上传文件")
            with col_header2:
                if st.button("📁 打开文件夹", key="open_project_docs", use_container_width=True):
                    open_folder(get_config(project).project_documents)
            
            files_uploaded = st.file_uploader("上传文件", accept_multiple_files=True, type=["txt", "doc", "docx", "epub", "md", 'pdf'], key="project_documents_files_uploader", label_visibility="hidden")
            if files_uploaded:
                for file_uploaded in files_uploaded:
                    file_bytes = file_uploaded.read()
                    with open(os.path.join(get_config(project).project_documents, file_uploaded.name), "wb") as f:
                        f.write(file_bytes)
                st.info("文件已全部保存，请及时更新知识库")
            
            st.subheader("文件列表")
            display_file_list_with_delete(get_config(project).project_documents, "project_documents")

    with tab2:
        context_documents = st.expander(f"项目: {project} - 上下文知识库", expanded=True)
        with context_documents:
            col_header1, col_header2 = st.columns([1, 1], vertical_alignment="center", gap="small")
            with col_header1:
                st.subheader("上传文件")
            with col_header2:
                if st.button("📁 打开文件夹", key="open_context_docs", use_container_width=True):
                    open_folder(get_config(project).context_documents)
            
            files_uploaded = st.file_uploader("上传文件", accept_multiple_files=True, type=["txt", "doc", "docx", "epub", "md", 'pdf'], key="context_documents_files_uploader", label_visibility="hidden")
            if files_uploaded:
                for file_uploaded in files_uploaded:
                    file_bytes = file_uploaded.read()
                    with open(os.path.join(get_config(project).context_documents, file_uploaded.name), "wb") as f:
                        f.write(file_bytes)
                st.info("文件已全部保存，请及时更新知识库")
            
            st.subheader("文件列表")
            display_file_list_with_delete(get_config(project).context_documents, "context_documents")

    with tab3:
        knowledge_documents = st.expander(f"项目: {project} - 背景知识库", expanded=True)
        with knowledge_documents:
            col_header1, col_header2 = st.columns([1, 1], vertical_alignment="center", gap="small")
            with col_header1:
                st.subheader("上传文件")
            with col_header2:
                if st.button("📁 打开文件夹", key="open_knowledge_docs", use_container_width=True):
                    open_folder(get_config(project).knowledge_documents)
            
            files_uploaded = st.file_uploader("上传文件", accept_multiple_files=True, type=["txt", "doc", "docx", "epub", "md", 'pdf'], key="knowledge_documents_files_uploader", label_visibility="hidden")
            if files_uploaded:
                for file_uploaded in files_uploaded:
                    file_bytes = file_uploaded.read()
                    with open(os.path.join(get_config(project).knowledge_documents, file_uploaded.name), "wb") as f:
                        f.write(file_bytes)
                st.info("文件已全部保存，请及时更新知识库")
            
            st.subheader("文件列表")
            display_file_list_with_delete(get_config(project).knowledge_documents, "knowledge_documents")