import tcvectordb
from tcvectordb.model.collection import Embedding
from tcvectordb.model.document import Document, Filter, SearchParams
from tcvectordb.model.enum import FieldType, IndexType, MetricType, EmbeddingModel
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, HNSWParams

# 初始化客户端
client = tcvectordb.VectorDBClient(url='http://your-vdb-url', username='your-username', key='your-api-key')

# 创建数据库和集合
database_name = 'text_db'
collection_name = 'text_collection'

db = client.create_database(database_name)

index = Index()
index.add(VectorIndex('vector', 768, IndexType.HNSW, MetricType.COSINE, HNSWParams(m=16, efconstruction=200)))
index.add(FilterIndex('id', FieldType.String, IndexType.PRIMARY_KEY))
index.add(FilterIndex('bookName', FieldType.String, IndexType.FILTER))
index.add(FilterIndex('author', FieldType.String, IndexType.FILTER))

embedding = Embedding(vector_field='vector', field='text', model=EmbeddingModel.BGE_BASE_ZH)

db.create_collection(
    name=collection_name,
    shard=1,
    replicas=1,
    description='Collection for text and embeddings',
    index=index,
    embedding=embedding
)

# 写入数据
documents = [
    Document(id='0001', text='富贵功名，前缘分定，为人切莫欺心。', bookName='西游记', author='吴承恩', page=21),
    Document(id='0002', text='正大光明，忠良善果弥深。些些狂妄天加谴，眼前不遇待时临。', bookName='西游记', author='吴承恩', page=22),
    Document(id='0003', text='细作探知这个消息，飞报吕布。', bookName='三国演义', author='罗贯中', page=23),
    Document(id='0004', text='布大惊，与陈宫商议。宫曰：“闻刘玄德新领徐州，可往投之。”布从其言，竟投徐州来。有人报知玄德。', bookName='三国演义', author='罗贯中', page=24),
    Document(id='0005', text='玄德曰：“布乃当今英勇之士，可出迎之。”糜竺曰：“吕布乃虎狼之徒，不可收留；收则伤人矣。', bookName='三国演义', author='罗贯中', page=25),
]

db.collection(collection_name).upsert(documents=documents)

# 查询数据
query_text = '细作探知这个消息，飞报吕布。'
search_params = SearchParams(ef=200)
filter_param = Filter('bookName="三国演义"')

results = db.collection(collection_name).searchByText(
    embeddingItems=[query_text],
    params=search_params,
    filter=filter_param,
    limit=3,
    retrieve_vector=False,
    output_fields=['id', 'bookName', 'author', 'text']
)

for result in results.get('documents'):
    for doc in result:
        print(doc)