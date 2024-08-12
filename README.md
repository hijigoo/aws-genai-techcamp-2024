# AWS GenAI TechCamp 2024

실제 업무 환경에서 사용할 수 있는 생성형 AI Chatbot 을 Bedrock 과 OpenSearch 를 이용해서 생성합니다.

- **completed**: 완성된 프로젝트로 모든 코드가 구현 되어 있습니다.
- **lab**: 실습을 위한 프로젝트로 주요 코드가 비어 있습니다.

## 0. 실습 해보기
실습을 위한 설명은 아래에서 확인할 수 있습니다.

1. [(Optional) AWS Cloud9 구성](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/0-aws-cloud9-setup.md)
2. [실습 프로젝트 구성](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/1-setting-project.md)
3. [OpenSearch 구성](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/2-setting-opensearch.md)
4. [Streamlit(UI) 코드 설명](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/3-streamlit-code.md)
5. [Normal Chat 구현](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/4-normal-chat.md)
6. [History Chat 구현](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/5-history-chat.md)
7. [RAG Chat 구현](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/6-RAG-chat.md)
8. [RAG Vector DB 확인](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/7-RAG-vector-db.md)
9. [SQL Chat 구현](https://github.com/hijigoo/aws-genai-techcamp-2024/blob/main/tutorial/8-SQL-chat.md)


## 1. 프로젝트 화면
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/f2759faa-4007-4533-9873-bcb0a761acab)
1. Bedrock API 에서 제공하는 파라미터값을 조절할 수 있습니다. 
2. RAG 환경에서 사용할 파일을 업로드 할 수 있습니다.
3. Chat 모드를 선택해서 채팅을 할 수 있습니다. 
4. 채팅을 할 수 있는 공간입니다.

## 2. Chat 모드
### 2-1. Normal 모드
입력에 대한 응답을 생성하는 일반적인 모드 입니다.
#### Sequence Diagram
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/934a89e4-7438-4fb5-8af5-7ec3cb07023f)
#### Example
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/495113d2-38a0-4e50-bf65-eb9460156044)

### 2-2. History 모드
대화 내용을 기억해서 응답을 생성하는 모드입니다.
#### Sequence Diagram
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/018535e2-16a0-4efa-ac0f-dbb7bc9192de)
#### Example
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/4558ff74-2136-4293-af78-5d28ed155717)

### 2-3. RAG 모드
Knowledge Base 에서  질문과 관련된 내용을 찾아서 응답을 생성합니다.
#### Sequence Diagram
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/d717dd50-7688-4697-984c-513384caf2e5)
#### Example
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/1c379755-8e9c-401d-b51d-acd7f1a198bf)

### 2-4. SQL 모드
질문에 대한 SQL Query 을 생성후 DB 를 호출해서 데이터를 얻고 응답을 생성합니다.
#### Sequence Diagram
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/f8d46e44-6a59-40ab-8c28-89b217854472)
#### Example
![image](https://github.com/hijigoo/aws-genai-techcamp-2024/assets/1788481/b6e7bf83-9b63-4696-a37b-010a736c19e1)

