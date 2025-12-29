"""
文件管理UI组件
从 pages/2_项目管理.py 提取的文件管理相关UI组件
"""
import os
import streamlit as st


def delete_file(filepath):
    """删除文件"""
    try:
        os.remove(filepath)
        st.toast(f"删除文件成功")
    except Exception as e:
        st.toast(f"删除文件失败: {e}")


def display_file_list_with_delete(folder_path, tab_name):
    """显示文件列表并支持删除"""
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
