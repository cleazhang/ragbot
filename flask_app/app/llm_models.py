# coding=utf-8
from typing import Optional, List, Any
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult, Generation
from openai import OpenAI
import time
from langchain_core.prompts import PromptTemplate
# LLMChain is deprecated in the new version; use prompt and llm directly
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
from langchain_core.documents import Document
import requests
from app.utils import load_embeddings,parse_pdf_to_documents,parse_html_to_documents

# Configuration: switch model via environment variables
LOCAL_LLM_URL = os.environ.get('LOCAL_LLM_URL', "http://localhost:8000/chat/completions")
USE_OPENAI = os.environ.get('USE_OPENAI', 'false').lower() == 'true'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')  # Using gpt-3.5-turbo is faster and cheaper

# SiliconFlow API configuration
USE_SILICONFLOW = os.environ.get('USE_SILICONFLOW', 'false').lower() == 'true'
SILICONFLOW_API_KEY = os.environ.get('SILICONFLOW_API_KEY', '')
SILICONFLOW_MODEL = os.environ.get('SILICONFLOW_MODEL', 'Qwen/QwQ-32B')
SILICONFLOW_API_URL = os.environ.get('SILICONFLOW_API_URL', 'https://api.siliconflow.cn/v1/chat/completions')

# Lazy-load embedding to avoid loading the model at import time (which may be slow)
_embedding = None
def get_embedding():
    global _embedding
    if _embedding is None:
        _embedding = load_embeddings()
    return _embedding

class ChatGlm3(BaseLLM):
    @property
    def _llm_type(self) -> str:
        return "chat-glm3"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        start_time = time.time()
        data = {
            "model": "chat-glm3",
            "messages": messages
        }
        try:
            completion = requests.post(LOCAL_LLM_URL, json=data, timeout=60)
            if completion.status_code == 200:
                result = completion.json()
                return_content = result['choices'][0]['message']['content']
            else:
                return_content = f"Error: {completion.status_code} - {completion.text}"
        except requests.exceptions.RequestException as e:
            return_content = f"Connection error: {str(e)}"
        print('Inference time', time.time() - start_time)
        return return_content
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate text"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)
    
class ChatGlm4(BaseLLM):
    @property
    def _llm_type(self) -> str:
        return "chat-glm4"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        start_time = time.time()
        data = {
            "model": "chat-glm4",
            "messages": messages
        }
        try:
            completion = requests.post(LOCAL_LLM_URL, json=data, timeout=60)
            if completion.status_code == 200:
                result = completion.json()
                return_content = result['choices'][0]['message']['content']
            else:
                return_content = f"Error: {completion.status_code} - {completion.text}"
        except requests.exceptions.RequestException as e:
            return_content = f"Connection error: {str(e)}"
        print('Inference time', time.time() - start_time)
        return return_content
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate text"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

class OpenAIModel(BaseLLM):
    """OpenAI API model with faster response"""
    @property
    def _llm_type(self) -> str:
        return "openai"
    
    def __init__(self):
        super().__init__()
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return_content = response.choices[0].message.content
        except Exception as e:
            return_content = f"OpenAI API error: {str(e)}"
        print('Inference time', time.time() - start_time)
        return return_content
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate text"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

class SiliconFlowModel(BaseLLM):
    """SiliconFlow API model"""
    @property
    def _llm_type(self) -> str:
        return "siliconflow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not SILICONFLOW_API_KEY:
            raise ValueError("SILICONFLOW_API_KEY environment variable is not set")
        self._api_key = SILICONFLOW_API_KEY
        self._api_url = SILICONFLOW_API_URL
        self._model = SILICONFLOW_MODEL
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        start_time = time.time()
        
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7,
            "n": 1
        }
        
        # Optional parameter, add only if supported
        if stop:
            payload["stop"] = stop
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self._api_url, json=payload, headers=headers, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return_content = result['choices'][0]['message']['content']
            else:
                return_content = f"SiliconFlow API error: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return_content = f"SiliconFlow API connection error: {str(e)}"
        except Exception as e:
            return_content = f"SiliconFlow API error: {str(e)}"
        
        print('Inference time', time.time() - start_time)
        return return_content
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate text"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

def get_llm():
    """Return the appropriate LLM instance based on configuration. Priority: SiliconFlow > OpenAI > local model"""
    # Prefer SiliconFlow API
    if USE_SILICONFLOW and SILICONFLOW_API_KEY:
        try:
            print("Using SiliconFlow API model")
            return SiliconFlowModel()
        except Exception as e:
            print(f"Unable to use SiliconFlow API: {e}, trying other models")
    
    # Next, try OpenAI API
    if USE_OPENAI and OPENAI_API_KEY:
        try:
            print("Using OpenAI API model")
            return OpenAIModel()
        except Exception as e:
            print(f"Unable to use OpenAI API: {e}, falling back to local model")
    
    # Default to local model
    print("Using local model")
    return ChatGlm4()

def get_answer_from_query(query, db, history):

    text_list = []
    if db is not None:
        similar_texts = db.similarity_search(query, include_metadata=True, k=4)
        text_list = ["Info" + str(index + 1) + '\n' + 'From file: ' + os.path.basename(d.metadata['source']) + '\n' + d.page_content for index, d in enumerate(similar_texts)]
        # print('text_list', text_list)
        context_text = '\n'.join(text_list)
    else:
        context_text = ''


    # Add history to the prompt
    if history:
        history_text = "\n".join([f"User: {item['query']}\nAssistant: {item['answer']}" for item in history])
    else:
        history_text = ''

    prompt_template = """You are a professional knowledge assistant dedicated to providing accurate and useful information. Your answer must be based on the retrieved document content and must remain faithful to the original text. If you find that the retrieved document content may be inaccurate or irrelevant to the question, honestly tell the user that you cannot provide an answer, and do not say anything else. If the question is beyond the scope of the retrieved content, you should honestly tell the user that you cannot provide an answer, and do not say anything else.
        Document content:
        {context}
        Conversation history:
        {history}
        Question:
        {query}"""
    
    # Format prompt
    formatted_prompt = prompt_template.format(
        context=context_text,
        history=history_text,
        query=query
    )
    
    # Use get_llm() to automatically select the model
    llm = get_llm()
    answer = llm.invoke(formatted_prompt)
    retrieved_result = text_list
    return {'answer': answer, 'retrieved_result': retrieved_result}


def update_db(files_path,db,embedding):
    all_split_docs = []
    print(files_path)
    for file_one in files_path:
        if file_one.endswith('.pdf'):
            split_docs=parse_pdf_to_documents(file_one)
            all_split_docs.extend(split_docs)
        # elif file_one.endswith('.html'):
        #     split_docs=parse_html_to_documents(file_one)
        #     all_split_docs.extend(split_docs)
        else:
            try:
                with open(file_one, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            except UnicodeDecodeError:
                with open(file_one, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()

            text_splitter = RecursiveCharacterTextSplitter(['\n\n','\n','。','，',''],chunk_size=256,chunk_overlap=32)
            chunks = text_splitter.split_text(raw_text)
            split_docs = [
                Document(page_content=chunk, metadata={'source': file_one})
                for chunk in chunks if chunk.strip()
            ]
            all_split_docs.extend(split_docs)

    db = FAISS.from_documents(all_split_docs, embedding)    
    # if db is not None:
    #     new_db = FAISS.from_documents(all_split_docs, embedding)
    #     db.merge_from(new_db)
    # else:
    #     db = FAISS.from_documents(all_split_docs, embedding)
    return db
