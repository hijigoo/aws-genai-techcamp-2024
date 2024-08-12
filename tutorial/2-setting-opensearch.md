# OpenSearch 구성

RAG Chat 구현에서 필요한 OpenSearch 는 생성이 완료되는데 20분 정도 소요되기 때문에 미리 생성해둡니다. 


## OpenSearch 클러스터 생성
### 1. AWS 콘솔에서 OpenSearch 를 검색해서 들어갑니다.

![image](https://github.com/user-attachments/assets/2196d693-f41b-4f88-a0fa-ede289de456b)


### 2. 왼쪽 메뉴에서 도메인(Domain) 이동 후 도메인 생성(Create domain) 선택합니다.

![image](https://github.com/user-attachments/assets/03877c4b-63cc-4de2-a471-577682b20d3c)


### 3. 환경 세부 정보를 설정합니다.
- 도메인 이름 : genai-techcamp-2024
- 도메인 생성 방법: 표준 생성 (Standard create)

![image](https://github.com/user-attachments/assets/8478eeb8-0bae-4938-aaa2-df62a02c49a6)

- 네트워크: 퍼블릭 액세스 (Public Access)

![image](https://github.com/user-attachments/assets/95a81bde-64e8-4ee0-a128-fd9c0b6b1267)

- 마스터 사용자: '마스터 사용자 생성' 선택
- 마스터 사용자 이름: [이름을 지정합니다] (예: techcamp2024)
- 마스터 암호: [암호를 지정합니다] (예: Passw0rd1!)

📗 지정한 [마스터 사용자 이름]과 [마스터 암호]는 코드에서 사용할 예정입니다. 메모장에 옮겨서 기록해 둡니다.

![image](https://github.com/user-attachments/assets/f42b2457-8b02-404c-afd3-e86d3042a297)

- 최대 절 수: 1024 (직접 입력합니다)

![image](https://github.com/user-attachments/assets/2c77b201-27a4-42b3-9445-9f830f9f6ad1)


오른쪽 메뉴에 있는 주황색 생성(Create) 버튼을 선택합니다.