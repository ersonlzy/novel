import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(
    page_title="主页",
    page_icon="✏️"
)
st.sidebar.success("主页")

st.write("# Novel Copilot")
st.markdown("""
This is a AI novel writer project maintained by ersonlzy@qq.com
""")