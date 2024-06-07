from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

from app import StreamHandler
import services.opensearch_service as os_svc

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
    return chat.invoke(
        {"input": messages}, {"callbacks": [stream_handler]}
    )['response']


def get_rag_conversation_response(
        chat: ConversationChain, content: str, stream_handler: BaseCallbackHandler
) -> tuple[str, str]:
    """
    Generate a response from the conversation chain with the given input.
    """
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
    result = chat.invoke(
        {"input": messages}, {"callbacks": [stream_handler]}
    )
    return result['response'], ":memo: ***Context*** :memo: \n ``` \n " + context + "\n ```"


def get_sql_conversation_response(
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
    return chat.invoke(
        {"input": messages}, {"callbacks": [stream_handler]}
    )['response']
