from abc import ABC
from typing import Dict
import streamlit as st

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_core.messages import HumanMessage, SystemMessage

from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import services.opensearch_service as os_svc
import services.bedrock_service as bedrock_svc

REGION_NAME = "us-west-2"


class StreamHandler(BaseCallbackHandler, ABC):
    """
    Callback handler to stream the generated text to Streamlit.
    """

    def __init__(self, container: st.container) -> None:
        self.container = container
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Append the new token to the text and update the Streamlit container.
        """
        self.text += token
        self.container.markdown(self.text)


def get_response(model_id: str, content: str, model_kwargs: Dict):
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )

    messages = [
        HumanMessage(
            content=content
        )
    ]

    stream_handler = StreamHandler(st.empty())

    # Option 1
    # response = ""
    # for chunk in chat.stream(messages):
    #     print(chunk)
    #     response += chunk.content
    #     stream_handler.on_llm_new_token(chunk.content)
    # return response

    # Option 2
    answer = llm.invoke(messages, {"callbacks": [stream_handler]}).content
    return answer


def get_conversation_response(
        model_id: str, content: str, memory_window: int, model_kwargs: Dict
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """

    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="input"),
        ]
    )

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

    messages = [
        HumanMessage(
            content=content
        )
    ]
    stream_handler = StreamHandler(st.empty())
    answer = chain.invoke(
        {"input": messages}, {"callbacks": [stream_handler]}
    )['response']

    return answer


def get_rag_conversation_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str]:
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )

    docs = os_svc.get_most_similar_docs_by_query(query=content, k=1)
    context = docs[0].page_content

    prompt = f"""
    다음 문맥을 사용하여 마지막 질문에 대한 간결한 답변을 제공하세요.
    답을 모르면 모른다고 말하고 답을 만들어내려고 하지 마세요.
    
    {context}
    
    질문: {content}
    """

    messages = [
        HumanMessage(
            content=prompt
        )
    ]

    stream_handler = StreamHandler(st.empty())

    answer = llm.invoke(
        messages, {"callbacks": [stream_handler]}
    ).content

    return answer, context


def get_sql_conversation_response(
        model_id: str, content: str, model_kwargs: Dict
) ->  tuple[str, str, str]:
    """
    Generate a response from the conversation chain with the given input.
    """

    # Make LLM instance
    llm = ChatBedrock(
        region_name="us-west-2",
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )

    # Make DB instance
    db = SQLDatabase.from_uri("sqlite:///db/Chinook.db")
    dialect = db.dialect
    table_info = db.table_info
    question = content

    # Make SQL generate prompt
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
    messages = [
        HumanMessage(
            content=prompt
        )
    ]

    # Invoke LLM and Get SQL query
    sql_query = llm.invoke(
        messages,
    ).content

    # Invoke SQL and Get result
    stream_handler = StreamHandler(st.empty())
    execute_query = QuerySQLDataBaseTool(db=db)
    sql_result = execute_query.invoke(sql_query)

    # Invoke LLM and Get final answer
    answer_prompt = f"""
    주어진 사용자의 질문에 대해서 아래 해당 SQL 쿼리 및 SQL 결과를 참고해서 답변해주세요.
    
    Question: {question}
    SQL Query: {sql_query}
    SQL Result: {sql_result}
    """

    messages = [
        HumanMessage(
            content=answer_prompt
        )
    ]

    answer = llm.invoke(
        messages, {"callbacks": [stream_handler]}
    ).content

    # How many employees are there
    return answer, sql_query, sql_result

