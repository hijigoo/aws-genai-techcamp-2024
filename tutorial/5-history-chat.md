# History Chat 구현

## 1. 함수 호출 흐름(Sequence Diagram)

![image](https://github.com/user-attachments/assets/65795d76-a522-4739-9571-17e5bf84e2e4)


## 2. get_conversation_chat_response() 메서드 코드 작성

🖥️ lab/services/chat_service.py 파일을 열어서 코드를 작성합니다.

ConversationChain 을 사용하면 아래와 같이 호출할 때 대화 내역을 자동으로 추가합니다.

```
Current conversation:

Human: Hi there!
AI Assistant: Hi there! It's nice to meet you. How can I help you today?
Human: [ 이번 입력 ]
```

[기존 코드]

```python
# TODO: History 를 기억하는 응답을 생성합니다.
def get_conversation_chat_response(
        model_id: str, content: str, memory_window: int, model_kwargs: Dict
) -> str:
    pass
```

[작성 코드]

```python
# History 를 기억하는 응답을 생성합니다.
def get_conversation_chat_response(
        model_id: str, content: str, memory_window: int, model_kwargs: Dict
) -> str:
    """
    Generate a response from the conversation chain with the given input.
    """
    # 1. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
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

    # 3. ConversationChain 을 호출해서 응답을 생성합니다.
    answer = conversation_chain.predict(input=content)
    return answer
```

## 3. 테스트

터미널에서 streamlit 명령을 실행합니다. 

```
cd ~/environment/aws-genai-techcamp-2024/lab/
streamlit run app.py --server.port 8080
```

Streamlit 명령으로 표시되는 네트워크 URL 및 외부 URL 링크는 무시합니다. 대신 AWS Cloud9의 미리보기 기능을 사용합니다. 

![image](https://github.com/user-attachments/assets/7ae193a5-3d7a-4dfd-a408-c15a8bedd15d)

아래와 같은 웹 화면이 표시됩니다.

![image](https://github.com/user-attachments/assets/6bad33b3-2a82-439c-b107-5b0ba7868d45)


왼쪽 메뉴 하단 메뉴에서 ⏳ History Chat 을 선택하고 지난 대화 내역을 기억하는지 테스트를 진행합니다.

![image](https://github.com/user-attachments/assets/0a20f882-5ee7-4edc-9bc8-06c036e69e94)
