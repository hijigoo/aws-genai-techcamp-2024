from typing import List, Tuple, Union

from langchain_aws import ChatBedrock
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

REGION_NAME = "us-west-2"
CLAUDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="input"),
    ]
)


def get_bedrock_chat(model_id, model_kwargs):
    return ChatBedrock(
        region_name=REGION_NAME,
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming=True
    )


def get_conversation_chat(llm, memory_window):
    # StreamlitChatMessageHistory will store messages in Streamlit session state at the specified key=.
    # The default key is "langchain_messages".
    # https://python.langchain.com/v0.2/docs/integrations/memory/streamlit_chat_message_history/
    return ConversationChain(
        llm=llm,
        memory=ConversationBufferWindowMemory(
            k=memory_window,
            ai_prefix="Assistant",
            chat_memory=StreamlitChatMessageHistory(),
            return_messages=True
        ),
        prompt=CLAUDE_PROMPT,
    )
