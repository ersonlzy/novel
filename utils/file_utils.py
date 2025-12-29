"""
文件操作工具模块
从 utils/tools.py 提取的文件操作相关功能
"""
import os
import streamlit as st


def get_documents_info(path):
    """获取文档信息"""
    files = os.listdir(path)
    data = {"文件": files}
    sizes = []
    for file in files:
        size = os.path.getsize(os.path.join(path, file)) / 1024 / 1024  # MB
        sizes.append(f"{size:.2f} MB")
    data.update({"文件大小": sizes})
    return data


@st.dialog("请确认操作")
def confirm(opearation, confirm_word, callback_fn):
    """确认对话框"""
    st.write(f"请确认操作:{opearation}，且操作不可逆")
    col311, col312 = st.columns([3, 1], gap="small", vertical_alignment="bottom")
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
