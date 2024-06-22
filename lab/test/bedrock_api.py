from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

# 1. ChatBedrock 을 생성합니다.
llm = ChatBedrock(
    region_name="us-east-1",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
)

# 2. ChatBedrock 에 전송할 메시지를 정의합니다.
question = "안녕?! 만가서 반가워"
messages = [
    HumanMessage(
        content=question
    )
]
print(question)

# 3. ChatBedrock 을 호출해서 응답을 생성합니다.
response = llm.invoke(messages)
print(response.content)
