from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

from app import StreamHandler


def get_response(chat: ChatBedrock, content: str, stream_handler: StreamHandler):
    messages = [
        HumanMessage(
            content=content
        )
    ]
    # response = ""
    # for chunk in chat.stream(messages):
    #     print(chunk)
    #     response += chunk.content
    #     stream_handler.on_llm_new_token(chunk.content)
    # return response

    return chat.invoke(messages, {"callbacks": [stream_handler]}).content


def get_conversation_response(
        chat: ConversationChain, content: str, stream_handler: BaseCallbackHandler
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """
    messages = [
        HumanMessage(
            content=content
        )
    ]
    return chat.invoke({"input": messages}, {"callbacks": [stream_handler]})['response']


def get_rag_conversation_response(
        conversation: ConversationChain, content: str, stream_handler: BaseCallbackHandler
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """
    input = [{"role": "user", "content": content}]
    return conversation.invoke(
        {"input": input}, {"callbacks": [stream_handler]}
    )


def get_sql_conversation_response(
        conversation: ConversationChain, content: str, stream_handler: BaseCallbackHandler
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """
    input = [{"role": "user", "content": content}]
    return conversation.invoke(
        {"input": input}, {"callbacks": [stream_handler]}
    )
