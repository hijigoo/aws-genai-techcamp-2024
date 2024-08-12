# SQL Chat 구현

## 1. 함수 호출 흐름(Sequence Diagram)

![image](https://github.com/user-attachments/assets/d4c70e0f-d8c5-45f3-a58f-43a8f4f1b2a7)

## 2. 샘플 DB

이번 프로젝트에서는 샘플 DB로 Chinook DB 파일을사용합니다. 파일은 /lab/db/chinook.db 에 있습니다.

> Chinook은 SQL Server, Oracle, MySQL 등에서 사용할 수 있는 샘플 데이터베이스입니다. 단일 SQL 스크립트를 실행하여 생성할 수 있습니다. Chinook 데이터베이스는 Northwind 데이터베이스의 대안으로, 단일 및 다중 데이터베이스 서버를 대상으로 하는 ORM 도구의 데모 및 테스트에 이상적입니다.

> Chinook DB: https://github.com/lerocha/chinook-database

## 3. get_sql_chat_response() 메서드 코드 작성

🖥️ lab/services/chat_service.py 파일을 열어서 코드를 작성합니다.

[기존 코드]

```python
# TODO: SQL 을 생성해서 데이터를 검색한 뒤 응답을 생성합니다.
def get_sql_chat_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str, str]:
    pass
```

[작성 코드]

```python
# SQL 을 생성해서 데이터를 검색한 뒤 응답을 생성합니다.
def get_sql_chat_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str, str]:
    """
    Generate a response from the conversation chain with the given input.
    """

    # 1. ChatBedrock 인스턴스를 생성합니다.
    # - 출력은 모아서 할 예정이기 때문에 Streaming 없이 생성합니다.
    llm = ChatBedrock(
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=False
    )

    # 2. DB instance 를 생성합니다.
    db = SQLDatabase.from_uri("sqlite:///db/Chinook.db")
    dialect = db.dialect
    table_info = db.table_info
    question = content

    # 3. SQL 생성을 위한 프롬프트를 정의합니다.
    # - dialect 에는 'sql' 이 들어갑니다.
    # - table_info 에는 table 스키마가 들어갑니다.
    # - question 에는 사용자 질문이 들어갑니다.
    prompt = f"""
        당신은 {dialect} 전문가입니다.
        회사의 데이터베이스에 대한 질문을 하는 사용자와 상호 작용하고 있습니다.
        아래의 데이터베이스 스키마를 기반으로 사용자의 질문에 답할 SQL 쿼리를 작성하세요.

        데이터베이스 스키마는 다음과 같습니다.
        <schema> {table_info} </schema>

        SQL 쿼리만 작성하고 다른 것은 작성하지 마세요.
        SQL 쿼리를 다른 텍스트로 묶지 마세요. 심지어 backtick 으로도 묶지 마세요.

        예시:
        Question: 10명의 고객 이름을 보여주세요.
        SQL Query: SELECT Name FROM Customers LIMIT 10;

        Your turn:
        Question: {question}
        SQL Query:
        """

    # 4. ChatBedrock 에 전송할 사용자 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=prompt
        )
    ]

    # 5. ChatBedrock 을 호출해서 SQL 생성을 요청합니다.
    sql_query = llm.invoke(
        messages,
    ).content

    # 6. SQL을 실행해서 데이터를 검색합니다.
    execute_query = QuerySQLDataBaseTool(db=db)
    sql_result = execute_query.invoke(sql_query)

    # 7. 최종 응답 생성을 위한 ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[StreamHandler(st.empty())]
    )

    # 8. 최종 응답을 생성하기 위한 프롬프트를 작성합니다
    # - question 에는 사용자 질문이 들어갑니다.
    # - sql_query 에는 실행한 query 가 들어갑니다.
    # - sql_result 에는 검색한 데이터가 들어갑니다.
    answer_prompt = f"""
    주어진 사용자의 질문에 대해서 아래 해당 SQL 쿼리 및 SQL 결과를 참고해서 답변해주세요.
    
    Question: {question}
    SQL Query: {sql_query}
    SQL Result: {sql_result}
    """

    # 9. ChatBedrock 에 전송할 사용자 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=answer_prompt
        )
    ]

    # 10. ChatBedrock 을 호출해서 최종 응답을 생성합니다.
    response = llm.invoke(messages)
    answer = response.content

    return answer, sql_query, sql_result
```

## 4. 테스트

터미널에서 Streamlit 명령을 실행합니다. 

```
cd ~/environment/aws-genai-techcamp-2024/lab/
streamlit run app.py --server.port 8080
```

Streamlit 명령으로 표시되는 네트워크 URL 및 외부 URL 링크는 무시합니다. 대신 AWS Cloud9의 미리보기 기능을 사용합니다. 

![image](https://github.com/user-attachments/assets/75e6b26f-d9be-4da0-9f7a-ed96a6bc504c)

아래와 같은 웹 화면이 표시됩니다.

![image](https://github.com/user-attachments/assets/0419dfcf-1a2e-4c26-a55c-f07f3042fa24)

왼쪽 메뉴 하단 메뉴에서 📊 SQL Chat 을 선택하고 SQL 을 생성 후 파일을 가져와서 응답 하는지 확인합니다.

Example1)

![image](https://github.com/user-attachments/assets/108c8129-2072-4f02-b6e8-96e78fbf7a3b)


Example2)

![image](https://github.com/user-attachments/assets/291703f4-acbb-4476-9bc1-b28b7510d8c5)
