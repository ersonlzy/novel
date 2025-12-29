"""
模型选择UI组件
从 pages/1_写作生成.py 提取的模型选择相关UI组件
"""
import streamlit as st
from config.settings import get_model_list


def get_model_list_safe(model_provider):
    """安全获取模型列表"""
    if model_provider is None:
        return ["请先选择模型服务商"]
    else:   
        res, model_list = get_model_list(model_provider)
        if res:
            return model_list
        else:
            # 显示具体错误信息
            st.error(model_list)
            return ["配置错误，请检查环境变量"]


def create_model_selector():
    """创建模型选择器"""
    model_provider_selection = st.selectbox(
        "模型配置", 
        options=["siliconflow", "deepseek", "dashscope", "openai", "ollama"], 
        index=None, 
        placeholder="请选择生成模型服务商", 
        label_visibility="collapsed"
    )
    model_selection = st.selectbox(
        "模型配置", 
        options=get_model_list_safe(model_provider_selection), 
        index=None, 
        placeholder="请选择生成模型", 
        label_visibility="collapsed"
    )
    
    return model_provider_selection, model_selection


def create_special_model_selector():
    """创建特殊模型选择器（用于提取器和缩写器）"""
    with st.expander("特殊模型配置", expanded=False):
        special_model_provider_selection = st.selectbox(
            "特殊模型服务商", 
            options=["siliconflow", "dashscope", "ollama"], 
            index=0, 
            placeholder="请选择模型服务商", 
            label_visibility="collapsed"
        )
        options = get_model_list_safe(special_model_provider_selection)
        index = options.index("Qwen/Qwen3-8B") if "Qwen/Qwen3-8B" in options else 0
        extractor_model_selection = st.selectbox(
            "检索提取模型", 
            options=options, 
            index=index, 
            placeholder="请选择提取器模型"
        )
        short_model_selection = st.selectbox(
            "内容缩写模型", 
            options=options, 
            index=index, 
            placeholder="请选择缩写器模型"
        )
    
    return special_model_provider_selection, extractor_model_selection, short_model_selection


def create_model_settings():
    """创建模型参数设置"""
    with st.expander("生成模型配置", expanded=True):
        temperature = st.slider("温度", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
        top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
        frequency_penalty = st.slider("重复生成惩罚", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
        presence_penalty = st.slider("已生成惩罚", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
    
    return {
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }
