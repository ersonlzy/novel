"""
输入卡片UI组件
从 pages/1_写作生成.py 提取的可复用UI组件
"""
import streamlit as st


def fullscreen_input_modal(key, placeholder, max_chars, current_value=""):
    """全屏输入模态框"""
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
    """创建输入卡片组件"""
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
