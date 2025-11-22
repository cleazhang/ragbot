import numpy as np
import faiss
from FlagEmbedding import BGEM3FlagModel
import pickle

embedding_model=BGEM3FlagModel('../llm_models/bge-m3',  
                       use_fp16=True) 

class VectorDB:
    def __init__(self):
        self.dimension = 0
        self.index = None
        self.doc_ids = []
        self.documents = []
        self.db=None

    def write_db(self, files_path):
        """
        将文档及其嵌入向量写入数据库。
        :param files_path: 文档路径列表。
        """
        all_split_docs = []

        # 文本读入，切分
        for file_one in files_path:
            print('Loading file', file_one)
            loader = UnstructuredFileLoader(file_one)
            data = loader.load()
            print(f'Documents loaded: {len(data)}')
            text_splitter = RecursiveCharacterTextSplitter(['\n\n', '\n', '。', '，', ''], chunk_size=256, chunk_overlap=32)
            split_docs = text_splitter.split_documents(data)
            all_split_docs.extend(split_docs)
            print('Total split documents:', len(all_split_docs))

        # 为所有分割的文档生成嵌入向量
        embeddings = [embedding_model.encode(doc.page_content)['dense_vecs'] for doc in all_split_docs]
        print('Embeddings:', embeddings)
        embeddings = np.array(embeddings)
        print('Embeddings generated:', embeddings.shape)

        self.dimension=embeddings[0]

        # 创建一个IndexIVFFlat索引
        quantizer = faiss.IndexFlatL2(self.dimension)  # 使用L2距离的Flat索引作为量化器
        clusters=min(len(all_split_docs),100) # 聚类数不超过文档数且最多为100
        index_ivf = faiss.IndexIVFFlat(quantizer, self.dimension, clusters)  

        # 训练索引
        print("Training IVF index")
        index_ivf.train(embeddings)

        # 添加向量到索引
        print("Adding vectors to IVF index")
        index_ivf.add(embeddings)

        # 创建IDMap索引
        index_id_map = faiss.IndexIDMap(index_ivf)

        # 为每个文档生成一个唯一的 ID
        doc_ids = np.arange(len(all_split_docs))

        # 将带有 ID 的嵌入向量添加到 IDMap 索引
        index_id_map.add_with_ids(embeddings, doc_ids)

        # 存储文档和向量
        self.documents = list(zip(all_split_docs, embeddings))

        # 创建FAISS向量存储
        if self.db is None:
            self.db = FAISS.from_embeddings([(d.page_content, e) for d, e in zip(all_split_docs, embeddings)], embedding_model)
        else:
            new_db = FAISS.from_embeddings([(d.page_content, e) for d, e in zip(all_split_docs, embeddings)], embedding_model)
            self.db.merge_from(new_db)


    def similarity_search(self, query_text, k=5):
        """
        查询数据库，返回与查询文本最相似的 k 个文档。
        :param query_text: 查询文本。
        :param k: 返回的最相似文档的数量。
        :return: 最相似的 k 个文档及其相似度分数。
        """
        # 将查询文本转换为嵌入向量
        query_embedding = embedding_model.encode(query_text)['dense_vecs']
        query_embedding = np.array(query_embedding).reshape(1, -1)

        # 执行查询
        distances, indices = self.index.search(query_embedding, k)

        # 获取最相似的文档及其相似度分数
        results = []
        for i in range(k):
            doc_id = indices[0][i]
            distance = distances[0][i]
            document = self.documents[doc_id]
            results.append((document, distance))

        return results


    def delete_vector(self, doc_id):
        """
        从数据库中删除指定的向量。
        :param doc_id: 要删除的向量的文档ID。
        """
        if doc_id in self.doc_ids:
            idx = self.doc_ids.index(doc_id)
            self.index.remove_ids(np.array([idx]))
            self.doc_ids.pop(idx)
            self.documents.pop(idx)
            print(f"Document with ID {doc_id} deleted.")
        else:
            print(f"Document with ID {doc_id} not found.")


    def update_vector(self, doc_id, new_content):
        """
        更新数据库中已有向量的内容。
        :param doc_id: 要更新的向量的文档ID。
        :param new_content: 新的文档内容。
        """
        if doc_id in self.doc_ids:
            idx = self.doc_ids.index(doc_id)
            new_embedding = embedding_model.encode(new_content)['dense_vecs']
            self.index.reconstruct(idx, new_embedding)
            self.documents[idx] = new_content
            print(f"Document with ID {doc_id} updated.")
        else:
            print(f"Document with ID {doc_id} not found.")


    def batch_insert(self, documents):
        """
        批量插入向量。
        :param documents: 文档列表。
        """
        embeddings = [embedding_model.encode(doc)['dense_vecs'] for doc in documents]
        embeddings = np.array(embeddings)
        doc_ids = np.arange(len(self.documents), len(self.documents) + len(documents))
        self.index.add_with_ids(embeddings, doc_ids)
        self.documents.extend(documents)
        self.doc_ids.extend(doc_ids)
        print(f"{len(documents)} documents inserted.")


    def rebuild_index(self):
        """
        重新构建索引。
        """
        embeddings = np.array([embedding_model.encode(doc)['dense_vecs'] for doc in self.documents])
        self.index.reset()
        self.index.train(embeddings)
        self.index.add_with_ids(embeddings, np.array(self.doc_ids))
        print("Index rebuilt.")


    def save_all(self, file_path = '/home/nameless0078/107rag_demo/db/db.pkl'):
        """
        将所有数据（索引、文档内容、文档ID）保存到文件。
        :param file_path: 文件路径。
        """
        # 将所有需要持久化的数据存储在一个字典中
        data_to_save = {
            'index': self.index,
            'documents': self.documents,
            'doc_ids': self.doc_ids
        }
        
        # 使用pickle将数据序列化并保存到文件
        with open(file_path, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"All data saved to {file_path}.")

    def load_all(self, file_path = '/home/nameless0078/107rag_demo/db/db.pkl'):
        """
        从文件加载所有数据。
        :param file_path: 文件路径。
        """
        # 使用pickle从文件加载数据
        with open(file_path, 'rb') as f:
            data_loaded = pickle.load(f)
        
        # 将加载的数据赋值回相应的属性
        self.index = data_loaded['index']
        self.documents = data_loaded['documents']
        self.doc_ids = data_loaded['doc_ids']
        
        print(f"All data loaded from {file_path}.")


    def get_statistics(self):
        """
        获取数据库的统计信息。
        :return: 统计信息字典。
        """
        stats = {
            "total_vectors": len(self.documents),
            "index_is_trained": self.index.is_trained,
            "index_ntotal": self.index.ntotal,
        }
        return stats



