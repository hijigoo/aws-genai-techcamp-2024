# RAG Chat 구현History Chat 구현

## 1. OpenSearch 추가 작업
OpenSearch 콘솔로 들어가서 생성이 완료된 도메인을 선택한 뒤 '보안 구성' 에서 '편집' 을 선택합니다.

![image](https://github.com/user-attachments/assets/2f765158-963b-4d78-83ee-8631791084a9)

도메인 수준 엑세스 정책 구성 에서 Effect : Allow 로 수정하고, 변경사항을 저장합니다.

![image](https://github.com/user-attachments/assets/5ea65b3d-bbc9-4bb7-86ad-aabf36337e58)

도메인 이름(Domain name) 과 엔드포인트(Domain endpoint) 를 메모장에 기록해 둡니다.

![image](https://github.com/user-attachments/assets/eda02e78-274b-4d77-8283-aea0006f3c32)


## 2. 함수 호출 흐름(Sequence Diagram)

PDF 를 Embedding 변환 하여 OpenSearch 에 Context 로 저장

![image](https://github.com/user-attachments/assets/373f3a7a-09aa-495b-9f87-29548121092f)


사용자 질문과 가장 관련 있는 Context 를 찾아서 응답 생성에 활용

![image](https://github.com/user-attachments/assets/10b1150b-38ce-495f-8548-470cbe4f62f6)


## 3. OpenSearch 관련 코드 작성

🖥️ lab/services/opensearch_service.py 파일을 열어서 코드를 작성합니다.

### 3-1. OpenSearch 정보를 설정

아래 기존 코드에서 OpenSearch 생성시 만들어진 정보를 입력합니다

```python
# TODO: OpenSearch 정보를 설정합니다.
opensearch_user_id = "[설정한 UserID]"
opensearch_user_password = "[설정한 User Password]"
opensearch_domain_endpoint = "[생성된 Domain Endpoint]"

opensearch_domain_name = "genai-techcamp-2024"
opensearch_index_name = "genai-techcamp-2024-index"
```

### 3-2. OpenSearch 사용에 필요한 기본 메서드 코드 작성

[기존 코드]

```python
# TODO: OpenSearch Client 를 생성합니다.
def get_opensearch_client():
    pass


# TODO: OpenSearch 에 인덱스가 있는지 확인합니다.
def check_if_index_exists() -> bool:
    pass


# TODO: OpenSearch 에 인덱스를 생성합니다.
def create_index():
    pass


# TODO: OpenSearch 에 인덱스를 삭제합니다.
def delete_index():
    pass


# TODO: OpenSearch 에 인덱스 리스트를 가져옵니다.
def get_index_list():
    pass
```


[작성 코드]

```python
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
```

### 3-3. OpenSearchVectorSearch Client 생성 코드 작성

[기존 코드]

```python
# TODO: OpenSearchVectorSearch Client 를 생성합니다.
def get_opensearch_vector_client():
    pass
```


[작성 코드]

```python
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
```

### 3-4. PDF 파일을 읽어서 Chunk 로 나눈 뒤 OpenSearch 에 저장하는 코드 작성

[기존 코드]

```python
# TODO: PDF 파일을 읽어서 페이지 단위로 chunk 를 나눠서 Document 를 만들고 OpenSearch 에 저장합니다.
def create_index_from_pdf_file(uploaded_file):
    pass


def create_index_from_documents(documents):
    pass
```


[작성 코드]

```python
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
```

### 3-5. OpenSearch 에서 가장 유사한 Document 를 가져오는 코드 작성

[기존 코드]

```python
# TODO: OpenSearch 에서 vector 유사도를 사용해서 가장 유사한 Document 를 가져옵니다.
def get_most_similar_docs_by_query(query: str, k: int):
    pass
```


[작성 코드]

```python
# OpenSearch 에서 vector 유사도를 사용해서 가장 유사한 Document 를 가져옵니다.
def get_most_similar_docs_by_query(query: str, k: int):
    osv_client = get_opensearch_vector_client()
    return osv_client.similarity_search(
        query,
        k=k,
    )
```

## 4. get_rag_chat_response() 메서드 코드 작성

🖥️ lab/services/chat_service.py 파일을 열어서 코드를 작성합니다.

[기존 코드]

```python
# TODO: Knowledge DB 로 부터 Context를 검색해서 응답을 생성합니다.
def get_rag_chat_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str]:
    pass
```


[작성 코드]

```python
# Knowledge DB 로 부터 Context를 검색해서 응답을 생성합니다.
def get_rag_chat_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str]:
    # 1. OpenSearch 에서 파일이 업로드 되어서 생성된 index 가 있는지 확인합니다.
    # - 업로드 된 파일이 없는 경우 리젝 응답이 나갑니다.
    if not os_svc.check_if_index_exists():
        return "업로드된 파일이 없습니다.", ""

    # 2. OpenSearch 에 Vector Search 를 해서 질문과 가장 관련된 Document 를 k 개 검색합니다.
    docs = os_svc.get_most_similar_docs_by_query(query=content, k=2)

    # 3. 가져온 Document 의 내용을 모아서 응답시 참고할 Context 를 만듭니다.
    context = ""
    for doc in docs:
        context += doc.page_content
        context += "\n\n"

    # 3. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[StreamHandler(st.empty())]
    )

    # 4. 프롬프트를 정의합니다.
    # - context 에는 검색한 내용이 들어갑니다.
    # - content 에는 질문이 들어갑니다.
    prompt = f"""
    다음 문맥을 사용하여 마지막 질문에 대한 간결한 답변을 제공하세요.
    답을 모르면 모른다고 말하고 답을 만들어내려고 하지 마세요.

    {context}

    질문: {content}
    """

    # 5. ChatBedrock 에 전송할 사용자 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=prompt
        )
    ]

    # 6. ChatBedrock 을 호출해서 응답을 생성합니다.
    response = llm.invoke(messages)
    answer = response.content

    return answer, context
```

## 5. 테스트

샘플로 사용할 PDF 파일을 준비합니다.

터미널에서 Streamlit 명령을 실행합니다. 

```
cd ~/environment/aws-genai-techcamp-2024/lab/
streamlit run app.py --server.enableXsrfProtection false --server.port 8080
```

Streamlit 명령으로 표시되는 네트워크 URL 및 외부 URL 링크는 무시합니다. 대신 AWS Cloud9의 미리보기 기능을 사용합니다. 

![image](https://github.com/user-attachments/assets/e69e7fb8-8e8b-4a97-9835-f6611e1834e1)

아래와 같은 웹 화면이 표시됩니다.

![image](https://github.com/user-attachments/assets/f9bc6164-7f04-4b9e-840c-8d798fe0e7bc)

왼쪽 메뉴에 있는 [Browse files] 버튼을 눌러서 다운 받은 파일을 선택한 뒤 [Upload to OpenSearch] 버튼을 눌러서 파일을 OpenSearch에 업로드 합니다. 이 때 파일은 페이지 단위로 Vector 생성 후 업로드 됩니다.

![image](https://github.com/user-attachments/assets/396a27a7-a1bd-4ed8-b380-1fe01dc38116)

왼쪽 메뉴 하단 메뉴에서 👓 RAG Chat 을 선택하고 업로드한 문서에서 관련된 응답을 하는지 확인합니다

![image](https://github.com/user-attachments/assets/2432b9c1-99d3-4541-880e-c57fd13cd29a)
