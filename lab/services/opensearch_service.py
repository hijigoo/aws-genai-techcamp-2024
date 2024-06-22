import boto3
import pdfplumber
from datetime import datetime
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import OpenSearch, RequestsHttpConnection
from langchain_community.embeddings import BedrockEmbeddings
from langchain_core.documents import Document

# TODO: OpenSearch 정보를 설정합니다.
opensearch_user_id = "[설정한 UserID]"
opensearch_user_password = "[설정한 User Password]"
opensearch_domain_endpoint = "[생성된 Domain Endpoint]"

opensearch_domain_name = "genai-techcamp-2024"
opensearch_index_name = "genai-techcamp-2024-index"


# TODO: OpenSearch 사용에 필요한 메서드를 정의합니다.
# OpenSearch Client 를 생성합니다.
def get_opensearch_client():
    pass


# OpenSearch 에 인덱스가 있는지 확인합니다.
def check_if_index_exists() -> bool:
    pass


# OpenSearch 에 인덱스를 생성합니다.
def create_index():
    pass


# OpenSearch 에 인덱스를 삭제합니다.
def delete_index():
    pass


# OpenSearch 에 인덱스 리스트를 가져옵니다.
def get_index_list():
    pass


# TODO: OpenSearchVectorSearch Client 를 생성합니다.
def get_opensearch_vector_client():
    pass


# TODO: PDF 파일을 읽어서 페이지 단위로 chunk 를 나눠서 Document 를 만들고 OpenSearch 에 저장합니다.
def create_index_from_pdf_file(uploaded_file):
    pass


# TODO: OpenSearch 에 Document 리스트를 저장합니다.
def create_index_from_documents(documents):
    pass


# TODO: OpenSearch 에서 vector 유사도를 사용해서 가장 유사한 Document 를 가져옵니다.
def get_most_similar_docs_by_query(query: str, k: int):
    pass
