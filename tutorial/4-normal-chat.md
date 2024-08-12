# Normal Chat 구현

## 1. 함수 호출 흐름(Sequence Diagram)

![image](https://github.com/user-attachments/assets/b8c9304a-3227-4823-bb16-09fd01967f93)


## 2. StreamHandler 클래스 코드 작성

🖥️ lab/services/chat_service.py 파일을 열어서 코드를 작성합니다.

Streaming 모드로 Bedrock 을 호출하는 경우 Token 단위로 응답이 오기 때문에 이를 처리해주어야 합니다. 여기서는 Langchain 에서 제공하는 BaseCallbackHandler 를 상속받아서 구현합니다. 새로운 토큰이 생성될 때마다 on_llm_new_token 함수가 호출됩니다. 함수가 호출되면 새로 생성되는 token 을 계속 연결하면서 화면에 출력합니다. 아래 제공하는 코드를 복사해서 기존 코드를 대체합니다. 

참고: https://python.langchain.com/v0.1/docs/modules/callbacks/

> StreamHandler 클래스는 모든 Chat 모드에서 사용됩니다.

[기존 코드]

```python
# TODO: 토큰 단위로 생성되는 스트리밍 텍스트를 출력하기 위한 콜백 핸들러 클래스를 정의합니다.
class StreamHandler(BaseCallbackHandler, ABC):
    pass
```

[작성 코드]

```python
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
```


## 3. get_chat_response() 메서드 코드 작성

🖥️ lab/services/chat_service.py 파일을 열어서 코드를 작성합니다.

[기존 코드]

```python
# TODO: 일반 응답을 생성합니다.
def get_chat_response(model_id: str, content: str, model_kwargs: Dict):
    pass
```

[작성 코드]

```python
# 일반 응답을 생성합니다.
def get_chat_response(model_id: str, content: str, model_kwargs: Dict):
    # 1. ChatBedrock 인스턴스를 생성합니다.
    llm = ChatBedrock(
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
```

## 4. 테스트

터미널에서 streamlit 명령을 실행합니다. 

```
cd ~/environment/aws-genai-techcamp-2024/lab/
streamlit run app.py --server.port 8080
```

Streamlit 명령으로 표시되는 네트워크 URL 및 외부 URL 링크는 무시합니다. 대신 AWS Cloud9의 미리보기 기능을 사용합니다. 

![image](https://github.com/user-attachments/assets/12fcc9dc-7612-498e-a7e2-96a354fc55b9)

아래와 같은 웹 화면이 표시됩니다.

![image](https://github.com/user-attachments/assets/e7000d12-829f-47cc-8e74-355ff487cb8d)

왼쪽 메뉴 하단에에서 🤖 Normal Chat 을 선택하고 아래와 같이 질문을 하면서 테스트를 진행합니다.

![image](https://github.com/user-attachments/assets/64d96680-b629-416e-980e-8cf08631de96)

