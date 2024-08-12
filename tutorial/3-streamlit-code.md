# Streamlit(UI) 코드 설명

UI 구현 부분은 핵심 내용은 아니기 때문에 주요 코드 설명으로 대체합니다.

이번 App 에서는 Streamlit 을 이용해서 UI 를 구현하고 비지니스 로직을 호출합니다. Streamlit 은 데이터 과학자와 AI/ML 엔지니어가 몇 줄의 코드만으로 대화형 데이터 앱을 제공할 수 있는 오픈소스 파이썬 프레임워크입니다. 

Streamlit 에는 고유한 데이터 흐름이 있습니다. 화면에서 무언가를 업데이트해야 할 때마다 파이썬 스크립트 전체를 처음부터 끝까지 다시 실행합니다. 예를 들어서 입력 상자에 텍스트를 입력하거나 버튼을 클릭할 때 스크립트를 처음부터 실행하여 UI 를 업데이트합니다. 앱의 소스 코드를 수정할 때도 동일하게 동작합니다.

🖥️ 전체 코드는 lab/app.py 에서 확인할 수 있습니다.

## 1. 화면의 타이틀과 AI 초기 메시지를 구합니다.
![image](https://github.com/user-attachments/assets/b88363f1-eee4-4e19-9f83-cea1fc0caa21)

```python
def set_page_config() -> None:
    """
    Set the Streamlit page configuration.
    """
    st.set_page_config(page_title="🤖 Chat with Bedrock", layout="wide")
    st.title("🤖 Chat with Bedrock")
```

```python
def init_chat_data() -> None:
    """
    Reset the chat session and initialize a new conversation chain.
    """
    init_message = {
        "role": "assistant",
        "content": "안녕하세요! 저는 Claude 3 챗봇 입니다. 무엇을 도와드릴까요?",
    }

    st.session_state.messages = []
    st.session_state["langchain_messages"] = []
    st.session_state.messages.append(init_message)
```


### 2. 왼쪽 메뉴의 파라미터 변경 / 파일 업로드 / Chat 모드 선택 화면을 구성합니다.

![image](https://github.com/user-attachments/assets/01022c9c-1b78-4fdb-9607-c90692a065e3)

#### 2-1. 파라미터 변경 화면

```python
def get_sidebar_params() -> Tuple[float, float, int, int, int, str]:
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

    return temperature, top_p, top_k, max_tokens, memory_window, model_id
```

#### 2-2. 파일 업로드 화면 (RAG 용)

로컬파일에서 파일을 선택한 뒤 업로드 버튼을 누르면 'create_index_from_pdf_file()' 함수를 호출합니다.

```python
def set_file_uploader():
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.sidebar.file_uploader("Upload your .pdf file", type={"pdf", "csv"},
                                             key=f"uploader_{st.session_state.uploader_key}")
    if uploaded_file is not None:
        btn = st.sidebar.button("Upload to OpenSearch", type="secondary")
        if btn:
            st.session_state.uploader_key += 1
            os_svc.create_index_from_pdf_file(uploaded_file=uploaded_file)
            st.rerun()
```

#### 2-3. Chat 모드 선택 화면

```python
def set_mode_selector():
    mode = st.sidebar.radio(
        "Generation Mode",
        [":robot_face: **Normal Chat**",
         ":hourglass_flowing_sand: **History Chat**",
         ":eyeglasses: **RAG Chat**",
         ":bar_chart: **SQL Chat**"],
        index=0,
    )
    return mode
```


### 3. 대화 내용을 출력합니다.

Streamlit 은 화면 업데이트 할 때 마다 파이썬 스크립트 전체를 처음부터 끝까지 다시 실행하기 때문에 대화 내용을 모두 저장하고 있다가 한 번에 보여줘야 합니다.

![image](https://github.com/user-attachments/assets/36d816af-ffae-4b98-8edb-1228b45bd641)


```python
def display_history_messages() -> None:
    """
    Display chat messages and uploaded images in the Streamlit app.
    """
    for message in st.session_state.messages:
        message_role = message["role"]
        with st.chat_message(message_role):
            message_content = message["content"]
            st.markdown(message_content)
```


### 4. main() : 사용자 입력을 받아서 화면에 출력하고 session에 저장합니다.

```python
# Get user input message
content = st.chat_input()

# Set new chat button
st.sidebar.button("Start New Chat", on_click=init_chat_data, type="primary")

# Display all history messages
display_history_messages()

# Store user message
if content:
    st.session_state.messages.append({"role": "user", "content": content})
    with st.chat_message("user"):
        st.markdown(content)
```


### 5. main() : 선택한 Chat 모드에 따라서 응답을 생성합니다.

```python
# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    # Get response
    with st.chat_message("assistant"):
        if "Normal Chat" in mode:
            response = chat_svc.get_chat_response(model_id=model_id, content=content,
                                                  model_kwargs=model_kwargs)

        if "History Chat" in mode:
            response = chat_svc.get_conversation_chat_response(model_id=model_id, content=content,
                                                               memory_window=memory_window,
                                                               model_kwargs=model_kwargs)
        elif "RAG Chat" in mode:
            response, context = chat_svc.get_rag_chat_response(model_id=model_id, content=content,
                                                               model_kwargs=model_kwargs)
            context = ":memo: ***Context*** :memo: \n\n" + context
            response = response + "\n\n" + context

        elif "SQL Chat" in mode:
            answer, sql_query, sql_result = chat_svc.get_sql_chat_response(model_id=model_id,
                                                                           content=content,
                                                                           model_kwargs=model_kwargs)
            sql_query = ":memo: ***Query*** :memo: \n ``` \n " + sql_query + "\n ```"
            sql_result = ":memo: ***Result*** :memo: \n ``` \n " + sql_result + "\n ```"
            response = answer + "\n\n" + sql_query + "\n\n" + sql_result

    # Store LLM generated responses
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
    st.rerun()
```