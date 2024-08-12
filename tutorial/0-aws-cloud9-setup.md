# AWS Cloud9 구성

이번 워크샵에서는 통합 개발 환경(IDE)으로 AWS Cloud9  을 사용합니다. AWS Cloud9은 Amazon Bedrock 으로 애플리케이션을 개발할 수 있는 옵션 중 하나이며, 자체 개발 도구(VS 코드, 파이참 등), Amazon SageMaker Studio  또는 주피터 노트북을 사용할 수도 있습니다.

아래에서는 생성형 AI 애플리케이션을 빌드하고 실행하기 위해 AWS Cloud9 환경 을 구성해 보겠습니다. 환경은 코드를 편집하고 터미널 명령을 실행하기 위한 웹 기반 통합 개발 환경을 의미합니다.

> AWS Cloud9는 Amazon Bedrock 파운데이션 모델이 활성화된 동일한 계정 및 리전에서 실행됩니다.

## AWS Cloud9 설정 방법
### 1. AWS 콘솔에서 Amazon Bedrock 파운데이션 모델이 활성화된 지역을 선택합니다.

![image](https://github.com/user-attachments/assets/9dbbacb7-9fec-49fb-ac9f-7e98a804b96e)


### 2. AWS 콘솔에서 Cloud9를 검색합니다.
- 검색 결과에서 Cloud9를 선택합니다.

![image](https://github.com/user-attachments/assets/bdce74b2-65ba-4436-bf70-5dabad797404)


### 3. Create environment을 클릭합니다.

![image](https://github.com/user-attachments/assets/a14b178e-22b0-466a-a8d0-ef339637805f)


### 4. 환경 세부 정보를 설정합니다.
- Name 을 bedrock-environment 로 설정합니다.

![image](https://github.com/user-attachments/assets/c5fa1492-15e1-47b6-9f55-76a3cfa4e140)


### 5. EC2 인스턴스 세부 정보를 설정합니다.
- 인스턴스 유형을 t3.small로 설정합니다.
- 플랫폼을 Ubuntu Server 22.04 LTS로 설정합니다.
- 시간 제한을 4시간으로 설정합니다.

![image](https://github.com/user-attachments/assets/a3804947-4300-420f-87bd-dba39d47df36)


### 6. Create 버튼을 선택합니다.

![image](https://github.com/user-attachments/assets/2ce0f86d-b033-4ffc-8cbd-fa0901a7d742)


### 7. 환경이 생성될 때까지 기다립니다.
- 준비가 완료되면 상단 배너에 "Successfully created bedrock-environment."라는 메시지가 표시됩니다.
- 환경 목록에서 Open 링크를 클릭합니다. 그러면 새 탭에서 AWS Cloud9 IDE가 시작됩니다.

> 환경 생성 오류 처리:  선택한 인스턴스 유형을 가용 영역에서 사용할 수 없다는 오류 메시지가 표시되면 환경을 삭제하세요. 다른 크기의 인스턴스 유형으로 프로비저닝을 다시 시도하세요.

![image](https://github.com/user-attachments/assets/fd902574-7eee-4d25-a595-94b9c16bf6e3)


### 8. AWS Cloud9 환경이 제대로 로드되었는지 확인합니다.
- Welcome 탭은 닫아도 됩니다.
- 탭을 원하는 위치로 끌어다 놓을 수 있습니다.

![image](https://github.com/user-attachments/assets/d4027518-cafb-4b87-8641-aebbd2e87c7a)

이 예제에서는 bash 터미널 탭을 위쪽 탭 스트립으로 드래그하고 아래쪽에 정렬된 패널을 닫았습니다.

![image](https://github.com/user-attachments/assets/32d8c6e9-bd25-419a-87f1-4c55a5b42b47)

AWS Cloud9을 성공적으로 구성하고 실행했습니다!