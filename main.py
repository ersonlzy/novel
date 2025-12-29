"""
Novel Copilot - AI 小说写作辅助工具
主入口文件 - 使用 Streamlit 多页面应用
"""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# 配置主页
st.set_page_config(
    page_title="Novel Copilot",
    page_icon="✏️",
    layout="wide"
)

# 主页内容
st.write("# Novel Copilot")
st.markdown("""
## AI 小说写作辅助工具

这是一个基于 RAG (检索增强生成) 技术的 AI 小说写作辅助工具。

### 功能特点

- **智能写作生成**: 基于大纲和设定自动生成小说章节
- **知识库管理**: 支持项目设定、上下文、背景知识的分类管理
- **多模型支持**: 支持多种 LLM 提供商（OpenAI、DeepSeek、SiliconFlow 等）
- **灵活配置**: 可自定义生成参数和模型选择

### 使用指南

1. **项目管理**: 创建或选择小说项目，上传相关知识库文件
2. **写作生成**: 输入大纲描述和用户要求，自动生成章节内容
3. **系统设置**: 配置模型参数和应用设置

---

**维护者**: ersonlzy@qq.com
""")

st.sidebar.success("请从侧边栏选择功能页面")