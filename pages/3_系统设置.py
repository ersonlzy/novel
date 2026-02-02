"""
系统设置页面
配置环境变量和API密钥
"""
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import shutil
from config.settings import get_model_list

st.set_page_config(page_title="系统设置", page_icon="⚙️", layout="wide")
st.markdown("# 系统设置")
st.sidebar.header("系统设置")

# 环境变量文件路径
ENV_PATH = Path(".env")
ENV_EXAMPLE_PATH = Path(".env.example")

# LLM 提供商配置
LLM_PROVIDERS = {
    "OPENAI": {"name": "OpenAI", "default_url": "https://api.openai.com/v1"},
    "OLLAMA": {"name": "Ollama", "default_url": "http://localhost:11434/"},
    "DEEPSEEK": {"name": "DeepSeek", "default_url": "https://api.deepseek.com/v1"},
    "DASHSCOPE": {"name": "DashScope (阿里云)", "default_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    "SILICONFLOW": {"name": "SiliconFlow", "default_url": "https://api.siliconflow.cn/v1/"},
    "ZHIPUAI": {"name": "智谱AI", "default_url": "https://open.bigmodel.cn/api/paas/v4"}
}


def load_env_config():
    """读取.env文件配置"""
    config = {}
    
    # 如果.env不存在，从.env.example复制
    if not ENV_PATH.exists() and ENV_EXAMPLE_PATH.exists():
        shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)
        st.info("已从 .env.example 创建 .env 文件")
    
    # 加载环境变量
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=True)
        
        # 读取生成参数
        config['MAX_GENERATE_NUM'] = os.getenv('MAX_GENERATE_NUM', '10')
        config['MAX_CHAPTERS_WORD_NUM'] = os.getenv('MAX_CHAPTERS_WORD_NUM', '6000')
        
        # 读取各个LLM提供商配置
        for provider in LLM_PROVIDERS.keys():
            config[f'{provider}_BASE_URL'] = os.getenv(f'{provider}_BASE_URL', '')
            config[f'{provider}_API_KEY'] = os.getenv(f'{provider}_API_KEY', '')

        # 读取嵌入模型配置
        config['DEFAULT_EMBEDDING_PROVIDER'] = os.getenv('DEFAULT_EMBEDDING_PROVIDER', '')
        config['DEFAULT_EMBEDDING_MODEL'] = os.getenv('DEFAULT_EMBEDDING_MODEL', '')

        # 读取重排序模型配置
        config['DEFAULT_RERANKER_PROVIDER'] = os.getenv('DEFAULT_RERANKER_PROVIDER', '')
        config['DEFAULT_RERANKER_MODEL'] = os.getenv('DEFAULT_RERANKER_MODEL', '')
    
    return config


def save_env_config(config):
    """保存配置到.env文件"""
    try:
        # 备份现有文件
        if ENV_PATH.exists():
            backup_path = ENV_PATH.with_suffix('.env.backup')
            shutil.copy(ENV_PATH, backup_path)
        
        # 写入所有配置
        for key, value in config.items():
            if value:  # 只保存非空值
                set_key(ENV_PATH, key, str(value))
        
        return True, "配置保存成功！"
    except Exception as e:
        return False, f"保存失败: {str(e)}"


def validate_url(url):
    """验证URL格式"""
    if not url:
        return True  # 允许空值
    return url.startswith('http://') or url.startswith('https://')


def validate_api_key(api_key, provider):
    """验证API Key格式"""
    if not api_key or api_key == "":
        return True  # 允许空值
    
    # Ollama不需要API Key
    if provider == "OLLAMA":
        return True
    
    # 基本格式检查
    if len(api_key) < 10:
        return False
    
    return True


# 加载当前配置
current_config = load_env_config()

# 创建Tab页
tab1, tab2, tab3 = st.tabs(["生成参数配置", "模型API配置", "默认模型配置"])

# Tab 1: 生成参数配置
with tab1:
    st.markdown("### 内容生成参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_generate_num = st.number_input(
            "最大生成章节数",
            min_value=1,
            max_value=50,
            value=int(current_config.get('MAX_GENERATE_NUM', 10)),
            help="单次可生成的最大章节数量"
        )
    
    with col2:
        max_chapters_word_num = st.number_input(
            "每章最大字数",
            min_value=100,
            max_value=20000,
            step=100,
            value=int(current_config.get('MAX_CHAPTERS_WORD_NUM', 6000)),
            help="每个章节可生成的最大字数"
        )
    
    if st.button("保存生成参数", key="save_gen_params", type="primary"):
        config_to_save = current_config.copy()
        config_to_save['MAX_GENERATE_NUM'] = str(max_generate_num)
        config_to_save['MAX_CHAPTERS_WORD_NUM'] = str(max_chapters_word_num)
        
        success, message = save_env_config(config_to_save)
        if success:
            st.success(message)
            st.info("配置已保存，需要重启应用才能生效")
        else:
            st.error(message)

# Tab 2: 模型API配置
with tab2:
    st.markdown("### LLM API密钥配置")
    st.info("提示：配置后需要重启应用才能生效。API Key 会安全存储在 .env 文件中。")
    
    # 用于收集所有配置的字典
    api_config = current_config.copy()
    
    # 为每个LLM提供商创建配置面板
    for provider_key, provider_info in LLM_PROVIDERS.items():
        with st.expander(f"{provider_info['name']}", expanded=False):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                base_url_key = f"{provider_key}_BASE_URL"
                base_url = st.text_input(
                    "Base URL",
                    value=current_config.get(base_url_key, provider_info['default_url']),
                    key=f"url_{provider_key}",
                    help=f"{provider_info['name']} API 的基础URL"
                )
                api_config[base_url_key] = base_url
                
                # URL验证
                if base_url and not validate_url(base_url):
                    st.error("URL格式无效，必须以 http:// 或 https:// 开头")
            
            with col2:
                api_key_key = f"{provider_key}_API_KEY"
                current_key = current_config.get(api_key_key, '')
                
                # 显示占位符或部分密钥
                placeholder = "未配置" if not current_key else f"{'*' * 20} (已配置)"
                
                api_key = st.text_input(
                    "API Key",
                    value=current_key,
                    type="password",
                    key=f"key_{provider_key}",
                    placeholder=placeholder,
                    help=f"{provider_info['name']} API密钥" + ("（Ollama本地部署无需配置）" if provider_key == "OLLAMA" else "")
                )
                api_config[api_key_key] = api_key
                
                # API Key验证
                if api_key and not validate_api_key(api_key, provider_key):
                    st.error("API Key格式无效")
                
                # 显示配置状态
                if current_key and current_key != "":
                    st.success("已配置")
                elif provider_key == "OLLAMA":
                    st.info("ℹ本地部署无需配置")
                else:
                    st.warning("未配置")
    
    # 保存按钮
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("保存所有API配置", key="save_all_api", type="primary"):
            success, message = save_env_config(api_config)
            if success:
                st.success(message)
                st.info("配置已保存，需要重启应用才能生效")
                st.balloons()
            else:
                st.error(message)
    
    with col2:
        if st.button("重置为默认值", key="reset_api"):
            if ENV_EXAMPLE_PATH.exists():
                shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)
                st.success("已重置为默认配置")
                st.info("⚠️ 请刷新页面查看更改")
            else:
                st.error(".env.example 文件不存在")

# Tab 3: 默认模型配置
with tab3:
    st.markdown("### 默认嵌入模型配置")
    st.info("配置系统默认使用的嵌入模型（Embedding Model），用于知识库检索等功能。")

    # 嵌入模型提供商选择
    embedding_provider_options = [""] + list(LLM_PROVIDERS.keys())
    # 尝试获取当前的 provider，如果不在选项中则默认为空
    current_emb_provider = current_config.get('DEFAULT_EMBEDDING_PROVIDER', '')
    if current_emb_provider not in embedding_provider_options:
        current_emb_provider = ""
        
    embedding_provider = st.selectbox(
        "选择嵌入模型提供商",
        options=embedding_provider_options,
        format_func=lambda x: LLM_PROVIDERS[x]['name'] if x in LLM_PROVIDERS else "未选择",
        index=embedding_provider_options.index(current_emb_provider) if current_emb_provider in embedding_provider_options else 0
    )

    # 模型选择
    embedding_model = current_config.get('DEFAULT_EMBEDDING_MODEL', '')
    model_options = [embedding_model] if embedding_model else []
    
    # 如果选择了提供商，尝试获取模型列表
    if embedding_provider:
        # 检查该提供商是否已配置 API Key / URL
        provider_base_url = current_config.get(f"{embedding_provider}_BASE_URL")
        provider_api_key = current_config.get(f"{embedding_provider}_API_KEY")
        
        # 简单的预检查，确保有配置才去请求
        if (embedding_provider == "OLLAMA" and provider_base_url) or (provider_api_key):
             with st.spinner(f"正在获取 {LLM_PROVIDERS[embedding_provider]['name']} 的模型列表..."):
                # 注意：这里假设 get_model_list 能正确处理 embedding 类型，或者我们获取所有模型后过滤
                # 通常 embedding 模型会有特定的标识，或者我们可以让用户自己输入如果获取失败
                # 暂时尝试获取 text/chat 类型，因为某些 API 可能不严格区分，或者我们传递 type="embedding"
                # 根据 config/settings.py 的定义：get_model_list(model_provider, type="text", sub_type="chat")
                # 我们尝试传 type="embedding"
                success, models = get_model_list(embedding_provider, type="all", sub_type="") 
                
                if success:
                     # 简单的过滤逻辑，如果能区分的话。目前简单列出所有或者是包含 'embedding' 的
                     # 这里先列出所有获取到的模型，让用户选择
                     model_options = models
                else:
                    st.warning(f"获取模型列表失败: {models}")
                    # 如果获取失败，允许手动输入，保留当前值
    
    # 使用 text_input 配合 datalist (streamlit 没有原生 datalist，用 selectbox + text_input 模拟或者直接 selectbox 可编辑模式 - st.selectbox 不支持编辑)
    # 为了灵活性，如果获取列表失败，我们应该允许用户手动输入。
    # Streamlit 的 selectbox 只有在 options 列表里才能选。
    # 我们可以用一个 checkbox "手动输入模型名称" 来切换
    
    use_manual_input = st.checkbox("手动输入模型名称", value=not bool(model_options) and bool(embedding_model))
    
    if use_manual_input:
        embedding_model_input = st.text_input(
            "嵌入模型名称",
            value=embedding_model,
            help="输入模型名称，例如: text-embedding-3-small"
        )
    else:
        # 确保当前值在选项中
        # model_options 应该是列表，如果 get_model_list 失败返回 False (bool)，我们需要确保它是列表
        if not isinstance(model_options, list):
             model_options = [embedding_model] if embedding_model else []
             
        if embedding_model and embedding_model not in model_options:
            model_options.append(embedding_model)
            
        embedding_model_input = st.selectbox(
            "选择嵌入模型",
            options=model_options,
            index=model_options.index(embedding_model) if embedding_model in model_options else 0 if model_options else None
        )

    st.markdown("---")
    st.markdown("### 默认重排序模型配置")
    st.info("配置系统默认使用的重排序模型（Reranker Model），用于优化知识库检索结果。")

    # 重排序模型提供商选择
    reranker_provider_options = [""] + list(LLM_PROVIDERS.keys())
    current_reranker_provider = current_config.get('DEFAULT_RERANKER_PROVIDER', '')
    if current_reranker_provider not in reranker_provider_options:
        current_reranker_provider = ""
        
    reranker_provider = st.selectbox(
        "选择重排序模型提供商",
        options=reranker_provider_options,
        format_func=lambda x: LLM_PROVIDERS[x]['name'] if x in LLM_PROVIDERS else "未选择",
        index=reranker_provider_options.index(current_reranker_provider) if current_reranker_provider in reranker_provider_options else 0
    )

    # 模型选择
    reranker_model = current_config.get('DEFAULT_RERANKER_MODEL', '')
    reranker_model_options = [reranker_model] if reranker_model else []
    
    if reranker_provider:
        provider_base_url = current_config.get(f"{reranker_provider}_BASE_URL")
        provider_api_key = current_config.get(f"{reranker_provider}_API_KEY")
        
        if (reranker_provider == "OLLAMA" and provider_base_url) or (provider_api_key):
             # 尝试获取模型，对于 rerank，有些厂商可能有特定标识，这里暂时也用 all
             with st.spinner(f"正在获取 {LLM_PROVIDERS[reranker_provider]['name']} 的模型列表..."):
                success, models = get_model_list(reranker_provider, type="all", sub_type="") 
                if success:
                     reranker_model_options = models
                else:
                    st.warning(f"获取模型列表失败: {models}")
    
    use_manual_input_reranker = st.checkbox("手动输入重排序模型名称", value=not bool(reranker_model_options) and bool(reranker_model))
    
    if use_manual_input_reranker:
        reranker_model_input = st.text_input(
            "重排序模型名称",
            value=reranker_model,
            help="输入模型名称，例如: bge-reranker-v2-m3"
        )
    else:
        if not isinstance(reranker_model_options, list):
             reranker_model_options = [reranker_model] if reranker_model else []
             
        if reranker_model and reranker_model not in reranker_model_options:
            reranker_model_options.append(reranker_model)
            
        reranker_model_input = st.selectbox(
            "选择重排序模型",
            options=reranker_model_options,
            index=reranker_model_options.index(reranker_model) if reranker_model in reranker_model_options else 0 if reranker_model_options else None
        )

    if st.button("保存默认模型配置", key="save_default_model", type="primary"):
        config_to_save = current_config.copy()
        config_to_save['DEFAULT_EMBEDDING_PROVIDER'] = str(embedding_provider) if embedding_provider else ""
        config_to_save['DEFAULT_EMBEDDING_MODEL'] = str(embedding_model_input) if embedding_model_input else ""
        config_to_save['DEFAULT_RERANKER_PROVIDER'] = str(reranker_provider) if reranker_provider else ""
        config_to_save['DEFAULT_RERANKER_MODEL'] = str(reranker_model_input) if reranker_model_input else ""
        
        success, message = save_env_config(config_to_save)
        if success:
            st.success(message)
            st.info("配置已保存")
        else:
            st.error(message)

# 底部信息
st.markdown("---")
st.markdown("""
### 配置说明

**文件位置**: `.env` 文件位于项目根目录

**安全提示**: 
- API Key 会以密码形式隐藏显示
- 所有配置存储在本地 `.env` 文件中
- 修改配置前会自动备份为 `.env.backup`

**使用建议**:
- 至少配置一个LLM提供商的API Key
- 推荐配置 SiliconFlow 用于检索功能
- Ollama 适合本地部署，无需API Key
""")