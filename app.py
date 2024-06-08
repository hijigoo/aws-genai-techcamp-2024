import random
from typing import List, Tuple, Union

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain

import services.bedrock_service as bedrock_svc
import services.chat_service as chat_svc
import services.opensearch_service as os_svc

INIT_MESSAGE = {
    "role": "assistant",
    "content": "안녕하세요! 저는 Claude 3 챗봇 입니다. 무엇을 도와드릴까요?",
}


class StreamHandler(BaseCallbackHandler):
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


def set_page_config() -> None:
    """
    Set the Streamlit page configuration.
    """
    st.set_page_config(page_title="🤖 Chat with Bedrock", layout="wide")
    st.title("🤖 Chat with Bedrock")


def init_chat_data() -> None:
    """
    Reset the chat session and initialize a new conversation chain.
    """
    st.session_state.messages = []
    st.session_state["langchain_messages"] = []
    st.session_state.messages.append(INIT_MESSAGE)


def get_sidebar_params() -> Tuple[float, float, int, int, int, str, str]:
    """
    Get inference parameters from the sidebar.
    """
    with st.sidebar:
        st.markdown("## Inference Parameters")
        model_id_select = st.selectbox(
            'Model',
            ('Claude 3 Sonnet', 'Claude 3 Haiku'),
            key=f"{st.session_state['widget_key']}_Model_Id",
        )

        model_map = {
            "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
            "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0"
        }

        model_id = model_map.get(model_id_select)
        system_prompt = ""
        # system_prompt = st.text_area(
        #     "System Prompt",
        #     "당신은 멋진 AI 입니다. 응답에 이모티콘 넣는 것을 좋아합니다.",
        #     key=f"{st.session_state['widget_key']}_System_Prompt",
        # )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.1,
            key=f"{st.session_state['widget_key']}_Temperature",
        )

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                top_p = st.slider(
                    "Top-P",
                    min_value=0.0,
                    max_value=1.0,
                    value=1.00,
                    step=0.01,
                    key=f"{st.session_state['widget_key']}_Top-P",
                )
            with col2:
                top_k = st.slider(
                    "Top-K",
                    min_value=1,
                    max_value=500,
                    value=500,
                    step=5,
                    key=f"{st.session_state['widget_key']}_Top-K",
                )
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                max_tokens = st.slider(
                    "Max Token",
                    min_value=0,
                    max_value=4096,
                    value=4096,
                    step=8,
                    key=f"{st.session_state['widget_key']}_Max_Token",
                )
            with col2:
                memory_window = st.slider(
                    "Memory Window",
                    min_value=0,
                    max_value=10,
                    value=10,
                    step=1,
                    key=f"{st.session_state['widget_key']}_Memory_Window",
                )

    return temperature, top_p, top_k, max_tokens, memory_window, model_id, system_prompt


def upload_file_to_opensearch():
    pass


def set_file_uploader():
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.sidebar.file_uploader("Upload your .pdf file", type="pdf",
                                             key=f"uploader_{st.session_state.uploader_key}")
    if uploaded_file is not None:
        btn = st.sidebar.button("Upload to OpenSearch", on_click=upload_file_to_opensearch, type="secondary")
        if btn:
            st.session_state.uploader_key += 1
            upload_pdf_as_vector(uploaded_file)
            st.rerun()


def get_conversation_chat(
        temperature: float,
        top_p: float,
        top_k: int,
        max_tokens: int,
        memory_window: int,
        model_id: str,
        system_prompt: str
) -> ConversationChain:
    """
    Initialize the ConversationChain with the given parameters.
    """
    model_kwargs = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
    }

    if system_prompt != "":
        model_kwargs["system"] = system_prompt

    chat = bedrock_svc.get_bedrock_chat(model_id=model_id, model_kwargs=model_kwargs)
    chat = bedrock_svc.get_conversation_chat(llm=chat, memory_window=memory_window)

    return chat


def display_history_messages() -> None:
    """
    Display chat messages and uploaded images in the Streamlit app.
    """
    for message in st.session_state.messages:
        message_role = message["role"]
        with st.chat_message(message_role):
            message_content = message["content"]
            st.markdown(message_content)


def convert_history_messages_for_memory() -> List[Union[AIMessage, HumanMessage]]:
    """
    Convert the messages for the LangChain conversation chain.
    """
    messages = st.session_state["langchain_messages"]

    for i, message in enumerate(messages):
        if isinstance(message.content, list):
            message_content = message.content[0]
            print(message_content)
            if "type" in message_content:
                if message_content["type"] == "ai":
                    message = AIMessage(message_content["content"])
                if message_content["type"] == "human":
                    message = HumanMessage(message_content["content"])
                messages[i] = message

    return messages


def upload_pdf_as_vector(uploaded_file):
    """PDF 파일을 받아서 Vector 로 변경 후 Opensearch Vector Store 에 저장.
    """
    return os_svc.create_index_from_pdf_file(uploaded_file=uploaded_file)


def delete_document_index(index_name: str):
    """OpenSearchIndex 제거
    """
    return os_svc.delete_index()


def main() -> None:
    """
    Main function to run the Streamlit app.
    """
    # Set page config
    set_page_config()

    # Initialize chat data
    if "messages" not in st.session_state:
        init_chat_data()

    # Generate a unique widget key only once
    if "widget_key" not in st.session_state:
        st.session_state["widget_key"] = str(random.randint(1, 1000000))

    # Set/Get sidebar params
    temperature, top_p, top_k, max_tokens, memory_window, model_id, system_prompt = get_sidebar_params()
    model_kwargs = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
    }

    # Get user input message
    content = st.chat_input()

    # Set file upload file
    set_file_uploader()

    # Get Mode
    mode = st.sidebar.radio(
        "Generation Mode",
        [":robot_face: **Normal**", ":hourglass_flowing_sand: **History**", ":eyeglasses: **RAG**",
         ":bar_chart: **SQL**"],
        index=0,
    )

    # Set new chat button
    st.sidebar.button("Start New Chat", on_click=init_chat_data, type="primary")

    # Display all history messages
    display_history_messages()

    # Convert history messages format for memory
    convert_history_messages_for_memory()

    # Store user message
    if content:
        st.session_state.messages.append({"role": "user", "content": content})
        with st.chat_message("user"):
            st.markdown(content)

    # Get chat
    chat = get_conversation_chat(temperature, top_p, top_k, max_tokens, memory_window, model_id, system_prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        # Get response
        with st.chat_message("assistant"):
            context = ""
            if "Normal" in mode:
                response = chat_svc.get_response(model_id=model_id, content=content, model_kwargs=model_kwargs)

            if "History" in mode:
                response = chat_svc.get_conversation_response(model_id=model_id, content=content,
                                                              memory_window=memory_window, model_kwargs=model_kwargs)
            elif "RAG" in mode:
                response, context = chat_svc.get_rag_conversation_response(model_id=model_id, content=content,
                                                                           model_kwargs=model_kwargs)
                context = ":memo: ***Context*** :memo: \n\n >" + context + "\n"
                response = response + "\n\n" + context
            elif "SQL" in mode:
                answer, sql_query, sql_result = chat_svc.get_sql_conversation_response(model_id=model_id,
                                                                                         content=content,
                                                                                         model_kwargs=model_kwargs)
                sql_query = ":memo: ***Query*** :memo: \n ``` \n " + sql_query + "\n ```"
                sql_result = ":memo: ***Result*** :memo: \n ``` \n " + sql_result + "\n ```"
                response = answer + "\n\n" + sql_query+ "\n\n" + sql_result

        # Store LLM generated responses
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
        st.rerun()


if __name__ == "__main__":
    main()
