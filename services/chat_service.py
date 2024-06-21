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
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import services.opensearch_service as os_svc


# 생성된 텍스트를 Streamlit에 스트리밍하기 위한 콜백 핸들러 클래스를 정의합니다.
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


# ChatBedrock 인스턴스를 통해서 일반 응답을 생성합니다.
def get_response(model_id: str, content: str, model_kwargs: Dict):
    # 1. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )

    # 2. ChatBedrock 에 전송할 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=content
        )
    ]

    # 3 . 스트림 응답을 받을 클래스를 생성합니다.
    stream_handler = StreamHandler(st.empty())

    # Option 1
    # 4. ChatBedrock 을 호출해서 응답을 요청합니다.
    # response = ""
    # for chunk in chat.stream(messages):
    #     print(chunk)
    #     response += chunk.content
    #     stream_handler.on_llm_new_token(chunk.content)
    # return response

    # Option 2
    # 4. ChatBedrock 을 호출해서 응답을 요청합니다.
    answer = llm.invoke(messages, {"callbacks": [stream_handler]}).content
    return answer


def get_conversation_response(
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
        streaming=True
    )

    # 2. ChatBedrock 에 전송할 메시지를 정의합니다.
    #  - history 에는 기록된 대화 내역이 자동으로 입력됩니다.
    #  - input 에는 ChatBedrock 에 전송할 메시지가 입력됩니다.
    prompt_template = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="input"),
        ]
    )

    # 3. 대화를 하고 메모리에서 대화 히스토리를 로드하는 체인을 생성합니다.
    # StreamlitChatMessageHistory will store messages in Streamlit session state at the specified key=.
    # The default key is "langchain_messages".
    chain = ConversationChain(
        llm=llm,
        memory=ConversationBufferWindowMemory(
            k=memory_window,
            ai_prefix="Assistant",
            chat_memory=StreamlitChatMessageHistory(),
            return_messages=True
        ),
        prompt=prompt_template,
    )

    # 4. ChatBedrock 에 전송할 사용자 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=content
        )
    ]

    # 5. 스트림 응답을 받을 클래스를 생성합니다.
    stream_handler = StreamHandler(st.empty())

    # 6. ConversationChain 을 호출해서 응답을 요청합니다.
    # - template 에 history 내용은 자동으로 입력됩니다.
    # - template 에 input 은 위에서 정의한 사용자 메시지로 입력합니다.
    answer = chain.invoke(
        {"input": messages}, {"callbacks": [stream_handler]}
    )['response']

    return answer


def get_rag_conversation_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str]:
    # 1. OpenSearch 에서 생성된 index 가 있는지 확인합니다.
    # - 파일 업로드할 때 생성됩니다.
    if not os_svc.check_if_index_exists():
        return "업로드된 파일이 없습니다.", ""

    # 2. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )

    # 3. Vector Search 를 해서 질문과 가장 관련된 Document 를 k 개 검색합니다.
    docs = os_svc.get_most_similar_docs_by_vector_query(query=content, k=1)
    context = docs[0].page_content

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

    # 6. 스트림 응답을 받을 클래스를 생성합니다.
    stream_handler = StreamHandler(st.empty())

    # 7. ChatBedrock 을 호출해서 응답을 요청합니다.
    answer = llm.invoke(
        # messages
        messages, {"callbacks": [stream_handler]}
    ).content

    return answer, context


def get_sql_conversation_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str, str]:
    """
    Generate a response from the conversation chain with the given input.
    """

    # 1. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
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
    stream_handler = StreamHandler(st.empty())
    execute_query = QuerySQLDataBaseTool(db=db)
    sql_result = execute_query.invoke(sql_query)

    # 7. 최종 응답을 생성하기 위한 프롬프트를 작성합니다
    # - question 에는 사용자 질문이 들어갑니다.
    # - sql_query 에는 실행한 query 가 들어갑니다.
    # - sql_result 에는 검색한 데이터가 들어갑니다.
    answer_prompt = f"""
    주어진 사용자의 질문에 대해서 아래 해당 SQL 쿼리 및 SQL 결과를 참고해서 답변해주세요.
    
    Question: {question}
    SQL Query: {sql_query}
    SQL Result: {sql_result}
    """

    # 8. ChatBedrock 에 전송할 사용자 메시지를 정의합니다.
    messages = [
        HumanMessage(
            content=answer_prompt
        )
    ]

    # 9. ChatBedrock 을 호출해서 최종 응답을 생성합니다.
    answer = llm.invoke(
        messages, {"callbacks": [stream_handler]}
    ).content

    return answer, sql_query, sql_result