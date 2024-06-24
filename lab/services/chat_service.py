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


# TODO: 토큰 단위로 생성되는 스트리밍 텍스트를 출력하기 위한 콜백 핸들러 클래스를 정의합니다.
class StreamHandler(BaseCallbackHandler, ABC):
    pass


# TODO: 일반 응답을 생성합니다.
def get_chat_response(model_id: str, content: str, model_kwargs: Dict):
    pass


# TODO: History 를 기억하는 응답을 생성합니다.
def get_conversation_chat_response(
        model_id: str, content: str, memory_window: int, model_kwargs: Dict
) -> str:
    pass


# TODO: Knowledge DB 로 부터 Context를 검색해서 응답을 생성합니다.
def get_rag_chat_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str]:
    pass


# TODO: SQL 을 생성해서 데이터를 검색한 뒤 응답을 생성합니다.
def get_sql_chat_response(
        model_id: str, content: str, model_kwargs: Dict
) -> tuple[str, str, str]:
    pass
