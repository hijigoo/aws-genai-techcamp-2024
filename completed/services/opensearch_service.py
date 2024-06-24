import boto3
import pdfplumber
from datetime import datetime
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import OpenSearch, RequestsHttpConnection
from langchain_community.embeddings import BedrockEmbeddings
from langchain_core.documents import Document

# OpenSearch 정보를 설정합니다.
opensearch_user_id = "techcamp2024"
opensearch_user_password = "Passw0rd1!"
opensearch_domain_endpoint = "https://search-genai-techcamp-2024-fa7cryrwnwnnjdturscmrnzhnu.us-west-2.es.amazonaws.com"

opensearch_domain_name = "genai-techcamp-2024"
opensearch_index_name = "genai-techcamp-2024-index"


# OpenSearch Client 를 생성합니다.
def get_opensearch_client():
    return OpenSearch(
        hosts=[
            {'host': opensearch_domain_endpoint.replace("https://", ""),
             'port': 443
             }
        ],
        http_auth=(opensearch_user_id, opensearch_user_password),  # Master username, Master password,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


# OpenSearch 에 인덱스가 있는지 확인합니다.
def check_if_index_exists() -> bool:
    os_client = get_opensearch_client()
    exists = os_client.indices.exists(opensearch_index_name)
    return exists


# OpenSearch 에 인덱스를 생성합니다.
def create_index():
    os_client = get_opensearch_client()
    os_client.indices.create(index=opensearch_index_name)


# OpenSearch 에 인덱스를 삭제합니다.
def delete_index():
    os_client = get_opensearch_client()
    return os_client.indices.delete(index=opensearch_index_name)


# OpenSearch 에 인덱스 리스트를 가져옵니다.
def get_index_list():
    os_client = get_opensearch_client()
    return os_client.indices.get_alias(index=opensearch_index_name)


# OpenSearchVectorSearch Client 를 생성합니다.
def get_opensearch_vector_client():
    # BedrockEmbeddings 클래스를 생성합니다.
    embedding = BedrockEmbeddings(
        client=boto3.client(service_name='bedrock-runtime'),
        model_id="amazon.titan-embed-g1-text-02"
    )

    # OpenSearchVectorSearch 클래스를 생성합니다.
    return OpenSearchVectorSearch(
        opensearch_url=opensearch_domain_endpoint,
        index_name=opensearch_index_name,
        embedding_function=embedding,
        is_aoss=False,
        connection_class=RequestsHttpConnection,
        http_auth=(opensearch_user_id, opensearch_user_password),
    )


# PDF 파일을 읽어서 페이지 단위로 chunk 를 나눠서 Document 를 만들고 OpenSearch 에 저장합니다.
def create_index_from_pdf_file(uploaded_file):
    print(f"current_pdf_file : {uploaded_file}")

    # 1. 사용될 변수를 정의하고 사용할 파일 이름과 타입을 추출합니다.
    docs = []
    source_name = uploaded_file.name.split('/')[-1]
    type_name = source_name.split('.')[-1]

    # 2. 지정된 경로에서 파일을 읽고 페이지 단위로 chunk 를 나눕니다.
    with pdfplumber.open(uploaded_file) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            chunk = Document(
                page_content=page_text.replace('\n', ' '),
                metadata={
                    "source": source_name,
                    "type": type_name,
                    "timestamp": datetime.now()
                }
            )
            docs.append(chunk)

    # 3. 인덱스를 생성하고 document 를 벡터와 함께 저장합니다.
    if len(docs) > 0:
        create_index_from_documents(documents=docs)


# OpenSearch 에 Document 리스트를 저장합니다.
def create_index_from_documents(documents):
    if check_if_index_exists():
        delete_index()

    # BedrockEmbeddings 클래스를 생성합니다.
    embedding = BedrockEmbeddings(
        client=boto3.client(service_name='bedrock-runtime'),
        model_id="amazon.titan-embed-g1-text-02"
    )

    # OpenSearchVectorSearch 클래스를 이용해서 인덱스를 생성하고 document 를 벡터와 함께 저장합니다.
    return OpenSearchVectorSearch.from_documents(
        documents=documents,
        embedding=embedding,
        opensearch_url=opensearch_domain_endpoint,
        timeout=300,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        http_auth=(opensearch_user_id, opensearch_user_password),
        index_name=opensearch_index_name,
    )


# OpenSearch 에서 vector 유사도를 사용해서 가장 유사한 Document 를 가져옵니다.
def get_most_similar_docs_by_query(query: str, k: int):
    osv_client = get_opensearch_vector_client()
    return osv_client.similarity_search(
        query,
        k=k,
    )
