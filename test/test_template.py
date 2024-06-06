from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import AIMessage, HumanMessage

print("# Test 1")
human_prompt = "Summarize our conversation so far in {word_count} words."
human_message_template = HumanMessagePromptTemplate.from_template(human_prompt)

chat_prompt = ChatPromptTemplate.from_messages(
    [human_message_template]
)
chat_val = chat_prompt.format_prompt(
    word_count="10"
)
print(chat_val.to_messages())
print(chat_val.to_string())
print()

print("# Test 2")
chat_prompt = ChatPromptTemplate.from_messages(
    [MessagesPlaceholder(variable_name="conversation")]
)

human_message = HumanMessage(content="What is the best way to learn programming?")
ai_message = AIMessage(content="Choose a programming language")

chat_val = chat_prompt.format_prompt(
    conversation=[human_message, ai_message]
)
print(chat_val.to_messages())
print(chat_val.to_string())
print()

print("# Test 3")
chat_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="user_message"),
    ]
)
chat_val = chat_prompt.format_prompt(user_message=[HumanMessage(content="안녕하세요")])
print(chat_val.to_messages())
print(chat_val.to_string())
print()

print("# Test 4")
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)

history = StreamlitChatMessageHistory(key="chat_messages")
history.add_user_message("hi!")
history.add_ai_message("whats up?")
print(history.messages)
print()
