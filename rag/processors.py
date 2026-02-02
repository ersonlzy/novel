from langchain_chroma import Chroma
from langchain_classic.text_splitter import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_classic.indexes import SQLRecordManager, index
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredEPubLoader, UnstructuredMarkdownLoader
import os
from tqdm import tqdm
import streamlit as st

from langchain_core.embeddings import Embeddings

class DocumentProcessor():
    
    def __init__(self, knowledge_base_path):
        self.embeddings: Embeddings
        # 获取默认嵌入模型配置
        emb_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "OLLAMA").upper()
        emb_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "qwen3-embedding:0.6b")
        
        if emb_provider == "OLLAMA":
            self.embeddings = OllamaEmbeddings(model=emb_model, base_url=os.getenv("OLLAMA_BASE_URL"))
        else:
            # 其他提供商通常使用 OpenAI 兼容 API
            # 注意：langchain_openai.OpenAIEmbeddings 默认使用 OPENAI_API_KEY 等
            # 如果是其他厂商，需要手动指定 base_url 和 api_key
            api_key = os.getenv(f"{emb_provider}_API_KEY")
            base_url = os.getenv(f"{emb_provider}_BASE_URL")
            self.embeddings = OpenAIEmbeddings(
                model=emb_model, 
                api_key=api_key, 
                base_url=base_url,
                check_embedding_ctx_length=False # 防止某些非OpenAI模型的长度检查错误
            )
        self.collection_name = knowledge_base_path.split("/")[-1]
        self.project_name = knowledge_base_path.split("/")[-2]
        self.sql_url = f"sqlite:///.db/{self.project_name}_{self.collection_name}_record_manager.db"
        self.knowledge_base_path = knowledge_base_path
        self.documents_dir = knowledge_base_path
        self.record_manager = SQLRecordManager(self.collection_name, db_url=self.sql_url)
        self.record_manager.create_schema()
        
        # 尝试加载已有的向量数据库
        vectordb_path = f".vectordb/{self.knowledge_base_path}/"
        try:
            # 检查向量数据库是否存在
            if os.path.exists(vectordb_path) and os.listdir(vectordb_path):
                self.chroma = Chroma(
                    collection_name=self.collection_name, 
                    persist_directory=vectordb_path, 
                    embedding_function=self.embeddings
                )
            else:
                # 向量数据库不存在，需要处理文档
                self.processing()
        except Exception as e:
            # 加载失败，重新处理文档
            print(f"加载向量数据库失败: {e}，将重新处理文档")
            self.processing()

    def processing(self):
        documents = [os.path.join(self.documents_dir, file) for file in os.listdir(self.documents_dir) if not file.startswith('.')]
        
        # 如果目录为空，创建空的 Chroma 实例
        if len(documents) == 0:
            st.toast(f"目录 {self.documents_dir} 中没有文档，已创建空知识库")
            self.chroma = Chroma(
                collection_name=self.collection_name, 
                persist_directory=f".vectordb/{self.knowledge_base_path}/", 
                embedding_function=self.embeddings
            )
            return
        
        all_contents = []
        for document in tqdm(documents): # type: ignore
            raw_contents = []
            try:
                if document.endswith(".txt"):
                    raw_contents = TextLoader(document, autodetect_encoding=True).load()
                elif document.endswith(".pdf"):
                    raw_contents = PyPDFLoader(document).load()
                elif document.endswith(".docx") or document.endswith(".doc"):
                    raw_contents = UnstructuredWordDocumentLoader(document).load()
                elif document.endswith(".epub"):
                    raw_contents = UnstructuredEPubLoader(document).load()
                elif document.endswith(".md"):
                    raw_contents = UnstructuredMarkdownLoader(document).load()
                else:
                    st.toast("未支持的文件格式, 仅支持txt, pdf, docx, doc, epub, md格式的文件")
                text_splitter = CharacterTextSplitter(separator="\n", chunk_size=200, chunk_overlap=20)
                contents = text_splitter.split_documents(raw_contents)
                all_contents.extend(contents)
            except Exception as e:
                st.toast(f"Processing encounter error with file {document}\nplease check the file is valid and its format.\n[Error] {e}")
        
        # 确保 self.chroma 已初始化
        if not hasattr(self, 'chroma'):
            self.chroma = Chroma(
                collection_name=self.collection_name, 
                persist_directory=f".vectordb/{self.knowledge_base_path}/", 
                embedding_function=self.embeddings
            )

        try:
            result = index(all_contents, self.record_manager, self.chroma, cleanup="incremental", source_id_key='source')
            st.toast(f"知识库更新成功\n新增知识块：{result['num_added']}\n删除知识块：{result['num_deleted']}\n更新知识块：{result['num_updated']}")
        except Exception as e:
            try:
                # 尝试重新创建（如果上面的更新失败）
                # 注意：Chroma.from_documents 会创建新的实例并持久化
                self.chroma = Chroma.from_documents(all_contents, self.embeddings, persist_directory=f".vectordb/{self.knowledge_base_path}/", collection_name=self.collection_name )
                result = index(all_contents, self.record_manager, self.chroma, cleanup="incremental", source_id_key='source')
                st.toast(f"知识库重建并更新成功\n新增知识块：{result['num_added']}\n删除知识块：{result['num_deleted']}\n更新知识块：{result['num_updated']}")
                st.toast(f"Processor has persisted all documents in path {self.knowledge_base_path}")
                st.toast(f"知识库{self.collection_name}处理成功")
            except Exception as e:
                st.toast(f"Processing encounter error with file {document}\nplease check the file is valid and its format.\n[Error] {e}")

    def get_Chroma(self) -> Chroma:
        return self.chroma
    
    def update(self):
        self.processing()
    