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
    # 初始化session_state
    if "model_provider" not in st.session_state:
        st.session_state.model_provider = None
    if "model_name" not in st.session_state:
        st.session_state.model_name = None
    
    # 计算当前索引
    providers = ["siliconflow", "deepseek", "dashscope", "openai", "ollama"]
    provider_index = None
    if st.session_state.model_provider in providers:
        provider_index = providers.index(st.session_state.model_provider)
    
    model_provider_selection = st.selectbox(
        "模型配置", 
        options=providers, 
        index=provider_index, 
        placeholder="请选择生成模型服务商", 
        label_visibility="collapsed",
        key="model_provider_selector"
    )
    
    # 更新session_state
    if model_provider_selection != st.session_state.model_provider:
        st.session_state.model_provider = model_provider_selection
        # 清空模型选择，因为提供商变了
        st.session_state.model_name = None
    
    # 获取模型列表并计算索引
    models = get_model_list_safe(model_provider_selection)
    model_index = None
    if st.session_state.model_name in models:
        model_index = models.index(st.session_state.model_name)
    
    model_selection = st.selectbox(
        "模型配置", 
        options=models, 
        index=model_index, 
        placeholder="请选择生成模型", 
        label_visibility="collapsed",
        key="model_name_selector"
    )
    
    # 更新session_state
    if model_selection != st.session_state.model_name:
        st.session_state.model_name = model_selection
    
    return model_provider_selection, model_selection


def create_special_model_selector():
    """创建特殊模型选择器（用于提取器和缩写器）"""
    with st.expander("特殊模型配置", expanded=False):
        special_model_provider_selection = st.selectbox(
            "特殊模型服务商", 
            options=["deepseek", "siliconflow", "dashscope", "ollama"], 
            index=None,  # 改为None，让用户明确选择
            placeholder="请选择模型服务商（留空则使用主模型配置）", 
            label_visibility="collapsed"
        )
        
        # 如果没有选择特殊模型，返回None
        if special_model_provider_selection is None:
            return None, None, None
        
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
    # 初始化session_state
    if "temperature" not in st.session_state:
        st.session_state.temperature = 1.0
    if "top_p" not in st.session_state:
        st.session_state.top_p = 1.0
    if "frequency_penalty" not in st.session_state:
        st.session_state.frequency_penalty = 0.0
    if "presence_penalty" not in st.session_state:
        st.session_state.presence_penalty = 0.0
    
    with st.expander("生成模型配置", expanded=True):
        temperature = st.slider(
            "温度", 
            min_value=0.0, 
            max_value=2.0, 
            value=st.session_state.temperature, 
            step=0.1,
            key="temperature_slider"
        )
        top_p = st.slider(
            "Top P", 
            min_value=0.0, 
            max_value=1.0, 
            value=st.session_state.top_p, 
            step=0.1,
            key="top_p_slider"
        )
        frequency_penalty = st.slider(
            "重复生成惩罚", 
            min_value=0.0, 
            max_value=2.0, 
            value=st.session_state.frequency_penalty, 
            step=0.1,
            key="frequency_penalty_slider"
        )
        presence_penalty = st.slider(
            "已生成惩罚", 
            min_value=0.0, 
            max_value=2.0, 
            value=st.session_state.presence_penalty, 
            step=0.1,
            key="presence_penalty_slider"
        )
    
    # 更新session_state
    st.session_state.temperature = temperature
    st.session_state.top_p = top_p
    st.session_state.frequency_penalty = frequency_penalty
    st.session_state.presence_penalty = presence_penalty
    
    return {
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }
