from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pdfplumber
import re
import uuid

def load_embeddings():
    """加载embedding模型"""
    import os
    from pathlib import Path
    
    # 获取项目根目录
    APP_DIR = Path(__file__).resolve().parent
    FLASK_ROOT = APP_DIR.parent
    PROJECT_ROOT = FLASK_ROOT.parent
    
    # 获取embedding模型路径和设备
    embedding_model_path = os.environ.get(
        'EMBEDDING_MODEL_PATH',
        str(PROJECT_ROOT / 'llm_models' / 'bge-m3')
    )
    embedding_device = os.environ.get('EMBEDDING_DEVICE', 'cpu')
    
    return HuggingFaceEmbeddings(
        model_name=embedding_model_path,
        model_kwargs={'device': embedding_device}
    )
    
class Document:
    def __init__(self, metadata, page_content , id=None):
        self.metadata = metadata
        self.page_content = page_content
        self.id = id if id else str(uuid.uuid4())  # 如果传入了 id，则使用传入的 id，否则生成一个新的 id

    def __str__(self):
        return f"Document(metadata={self.metadata}, page_content={self.page_content}, id={self.id})"
    
def parse_pdf_to_documents(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        documents = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                metadata = {'source': f'../uploads/{pdf_path}'}
                page_content = text.strip()
                documents.append(Document(metadata, page_content))
    return documents

def clean_text(text):
    # 清理文本中的无效字符和空格
    text = text.replace('\xa0', '').replace('\n', '').strip()
    text = re.sub(r'\s+', ' ', text)  # 将多个连续空格替换为一个空格
    return text

def parse_html_to_documents(file_path):
    # 使用 BSHTMLLoader 加载文件
    loader = BSHTMLLoader(file_path, open_encoding='utf-8')
    data = loader.load()
    
    # 使用 RecursiveCharacterTextSplitter 进行文本分割
    text_splitter = RecursiveCharacterTextSplitter(['\n\n', '\n', '。', '，', '', " "], chunk_size=256, chunk_overlap=32)
    corpus = text_splitter.split_text(data)
    
    # 清理分割后的文本内容
    texts = [clean_text(text) for text in corpus]
    texts = [text for text in texts if len(text) >= 8]
    
    # 创建 Document 对象并添加元数据
    documents = []
    for text in texts:
        metadata = {'source': file_path}
        documents.append(Document(metadata, text))

    
    print('---------------------------------------------------')
    print('documents',documents)
    print('---------------------------------------------------')
    return documents

def store_feedback_to_file(feedback_data):
    # 指定文件名和路径
    file_path = 'feedback.txt'
    
    # 以追加模式打开文件，以便每次请求都添加到文件末尾
    with open(file_path, 'a') as file:
        file.write(feedback_data)