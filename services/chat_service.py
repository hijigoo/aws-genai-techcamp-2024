from abc import ABC
from typing import Dict
import streamlit as st

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_core.messages import HumanMessage

from langchain_community.utilities import SQLDatabase

import services.opensearch_service as os_svc


# 토큰 단위로 생성되는 스트리밍 텍스트를 출력하기 위한 콜백 핸들러 클래스를 정의합니다.
class StreamHandler(BaseCallbackHandler, ABC):
    """
    Callback handler to stream the generated text to Streamlit.
    """

    # 생성자에서는 Streamlit 컨테이너와 빈 문자열을 초기화합니다.
    def __init__(self, container: st.container) -> None:
        self.container = container
        self.text = ""

    # 새로운 토큰이 생성될 때마다 호출되며, 생성된 텍스트에 토큰을 추가하고 Streamlit 컨테이너를 업데이트합니다.
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Append the new token to the text and update the Streamlit container.
        """
        self.text += token
        self.container.markdown(self.text)


# 일반 응답을 생성합니다.
def get_chat_response(model_id: str, content: str, model_kwargs: Dict):
    # 1. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[StreamHandler(st.empty())]
    )

    # 2. ChatBedrock 에 전송할 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=content
        )
    ]

    # 3. ChatBedrock 을 호출해서 응답을 생성합니다.
    response = llm.invoke(messages)
    answer = response.content
    return answer


# History 를 기억하는 응답을 생성합니다.
def get_conversation_chat_response(
        model_id: str, content: str, memory_window: int, model_kwargs: Dict
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """
    # 1. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[StreamHandler(st.empty())]
    )

    # 2. 대화를 하고 메모리에서 대화 히스토리를 로드하는 체인을 생성합니다.
    # StreamlitChatMessageHistory will store messages in Streamlit session state at the specified key=.
    # The default key is "langchain_messages".
    conversation_chain = ConversationChain(
        llm=llm,
        memory=ConversationBufferWindowMemory(
            k=memory_window,
            ai_prefix='Assistant',
            chat_memory=StreamlitChatMessageHistory(),
            return_messages=True
        ),
        verbose=True
    )

    # 6. ConversationChain 을 호출해서 응답을 생성합니다.
    answer = conversation_chain.predict(input=content)
    return answer


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
        region_name="us-west-2",
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
        region_name="us-west-2",
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
        region_name="us-west-2",
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
