from datetime import datetime
import boto3
import pdfplumber
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import OpenSearch, RequestsHttpConnection
from langchain_community.embeddings import BedrockEmbeddings
from langchain_core.documents import Document

# OpenSearch 인증 정보를 설정합니다.
opensearch_user_id = "USER_ID"
opensearch_user_password = "USER_PASSWORD"
opensearch_domain_name = "genai-techcamp-2024"
opensearch_domain_endpoint = "https://search-genai-techcamp-2024-fa7cryrwnwnnjdturscmrnzhnu.us-west-2.es.amazonaws.com"
opensearch_http_auth = (opensearch_user_id, opensearch_user_password)

# OpenSearch 의 index 이름을 선언합니다. (DB의 테이블이라고 생각하시면 편합니다.)
index_name = "genai-techcamp-2024-index"


# Bedrock Embeddings 을 가져옵니다.
def get_bedrock_embedding():
    embedding = BedrockEmbeddings(
        client=boto3.client(service_name='bedrock-runtime'),
        model_id="amazon.titan-embed-g1-text-02"
    )
    return embedding


# OpenSearch 클라이언트를 가져오는 함수를 정의합니다.
def get_opensearch_client():
    return OpenSearch(
        hosts=[
            {'host': opensearch_domain_endpoint.replace("https://", ""),
             'port': 443
             }
        ],
        http_auth=opensearch_http_auth,  # Master username, Master password,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


# OpenSearch 의 인덱스 존재 여부를 확인하는 함수를 정의합니다.
def check_if_index_exists() -> bool:
    os_client = get_opensearch_client()
    exists = os_client.indices.exists(index_name)
    return exists


# OpenSearch 의 인덱스를 생성하는 함수를 정의합니다.
def create_index():
    os_client = get_opensearch_client()
    os_client.indices.create(index=index_name)


# OpenSearch 의 인덱스를 삭제하는 함수를 정의합니다.
def delete_index():
    os_client = get_opensearch_client()
    return os_client.indices.delete(index=index_name)


# OpenSearch 의 인덱스 목록을 가져오는 함수를 정의합니다.
def get_index_list():
    os_client = get_opensearch_client()
    return os_client.indices.get_alias(index=index_name)


# OpenSearch 의 벡터 클라이언트를 가져오는 함수를 정의합니다.
def get_opensearch_vector_client():
    embedding = get_bedrock_embedding()
    return OpenSearchVectorSearch(
        opensearch_url=opensearch_domain_endpoint,
        index_name=index_name,
        embedding_function=embedding,
        is_aoss=False,
        connection_class=RequestsHttpConnection,
        http_auth=opensearch_http_auth,
    )


# 업로드된 PDF 파일에서 인덱스를 생성하는 함수를 정의합니다.
def create_index_from_uploaded_file(uploaded_file):
    print("Start upload PDF file")
    print(f"current_pdf_file : {uploaded_file}")

    # 1. 파일 이름을 추출합니다.
    source_name = uploaded_file.name.split('/')[-1]

    # 2. 파일의 확장자를 추출합니다.
    type_name = source_name.split('.')[-1]

    # 3. OpenSearch 에 넣을 문서가 들어갈 배열을 선언합니다.
    docs = []

    # 4. PdfPlumber 라이브러리를 이용해서 PDF 를 읽어옵니다.
    with pdfplumber.open(uploaded_file) as pdf:
        # 4-1. 한 페이지씩 읽어옵니다.

        for page_number, page in enumerate(pdf.pages, start=1):
            # 4-2. 페이지에서 텍스트를 읽어옵니다.
            page_text = page.extract_text()
            if len(page_text) == 0:
                continue

            # 4-3. 한 페이지씩 Document 를 만들어서 Chunk로 사용합니다.
            chunk = Document(
                page_content=page_text.replace('\n', ' '),
                metadata={
                    "source": source_name,
                    "type": type_name,
                    "timestamp": datetime.now()
                }
            )
            docs.append(chunk)

    # 5. OpenSearch 에 문서(Documents)들을 입력합니다.
    if len(docs) > 0:
        create_index_from_documents(documents=docs)


# 문서 목록에서 인덱스를 생성하는 함수를 정의합니다.
def create_index_from_documents(documents):
    if check_if_index_exists():
        delete_index()

    embedding = get_bedrock_embedding()
    return OpenSearchVectorSearch.from_documents(
        documents=documents,
        embedding=embedding,
        opensearch_url=opensearch_domain_endpoint,
        timeout=300,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        http_auth=opensearch_http_auth,
        index_name=index_name,
    )


# 벡터 쿼리로 가장 유사한 문서를 가져오는 함수를 정의합니다.
def get_most_similar_docs_by_vector_query(query: str, k: int):
    osv_client = get_opensearch_vector_client()
    return osv_client.similarity_search(
        query,
        k=k,
    )


# 벡터 쿼리로 가장 유사한 문서와 점수를 가져오는 함수를 정의합니다.
def get_most_similar_docs_by_vector_query_with_score(query: str, k: int):
    osv_client = get_opensearch_vector_client()
    return osv_client.similarity_search_with_score(
        query,
        k=k,
    )
