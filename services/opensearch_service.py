from datetime import datetime

import boto3
import pdfplumber
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import OpenSearch, RequestsHttpConnection
from langchain_community.embeddings import BedrockEmbeddings
from langchain_core.documents import Document

opensearch_user_id = "USER_ID"
opensearch_user_password = "PASSWORLD"
opensearch_domain_name = "genai-techcamp-2024"
opensearch_domain_endpoint = "https://search-genai-techcamp-2024-fa7cryrwnwnnjdturscmrnzhnu.us-west-2.es.amazonaws.com"

http_auth = (opensearch_user_id, opensearch_user_password)

index_name = "genai-techcamp-2024-index"
embedding = BedrockEmbeddings(
    client=boto3.client(service_name='bedrock-runtime'),
    model_id="amazon.titan-embed-g1-text-02"
)


# OpenSearch Client
def get_opensearch_client():
    return OpenSearch(
        hosts=[
            {'host': opensearch_domain_endpoint.replace("https://", ""),
             'port': 443
             }
        ],
        http_auth=http_auth,  # Master username, Master password,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def check_if_index_exists() -> bool:
    os_client = get_opensearch_client()
    exists = os_client.indices.exists(index_name)
    return exists


def create_index():
    os_client = get_opensearch_client()
    os_client.indices.create(index=index_name)


def delete_index():
    os_client = get_opensearch_client()
    return os_client.indices.delete(index=index_name)


def get_index_list():
    os_client = get_opensearch_client()
    return os_client.indices.get_alias(index=index_name)


# OpenSearchVectorSearch Client
def get_opensearch_vector_client():
    return OpenSearchVectorSearch(
        opensearch_url=opensearch_domain_endpoint,
        index_name=index_name,
        embedding_function=embedding,
        is_aoss=False,
        connection_class=RequestsHttpConnection,
        http_auth=http_auth,
    )


def create_index_from_pdf_file(uploaded_file):
    print(f"current_pdf_file : {uploaded_file}")

    if check_if_index_exists():
        delete_index()
    create_index()

    docs = []
    source_name = uploaded_file.name.split('/')[-1]
    type_name = source_name.split('.')[-1]

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
    if len(docs) > 0:
        create_index_from_documents(documents=docs)


def create_index_from_documents(documents):
    if check_if_index_exists():
        delete_index()

    return OpenSearchVectorSearch.from_documents(
        documents=documents,
        embedding=embedding,
        opensearch_url=opensearch_domain_endpoint,
        timeout=300,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        http_auth=http_auth,
        index_name=index_name,
    )


def get_most_similar_docs_by_query(query: str, k: int):
    osv_client = get_opensearch_vector_client()
    return osv_client.similarity_search(
        query,
        k=k,
    )


def get_most_similar_docs_by_query_with_score(query: str, k: int):
    osv_client = get_opensearch_vector_client()
    return osv_client.similarity_search_with_score(
        query,
        k=k,
    )
