# 실습 프로젝트 구성

## 실습 프로젝트 다운로드 및 구성
### 1. AWS Cloud9 IDE에서 bash terminal을 선택합니다.

![image](https://github.com/user-attachments/assets/781c80f6-aed6-4570-8775-a9ec5db33598)


### 2. 터미널에 다음을 붙여넣고 실행하여 코드를 다운로드(clone)합니다.
```
cd ~/environment/
git clone https://github.com/hijigoo/aws-genai-techcamp-2024.git
```

정상적으로 다운 받으면 아래와 같은 구조를 확인할 수 있습니다. 
- completed 디렉토리에는 완성된 프로젝트가 있습니다.
- lab 디렉토리에는 실습할 프로젝트가 있습니다.

![image](https://github.com/user-attachments/assets/1e8a3f66-e63d-4890-b339-43bc5c9ccc61)


### 3. 실습에 필요한 종속성을 설치합니다.
```
pip3 install -r ~/environment/aws-genai-techcamp-2024/requirements.txt -U
```

모든 것이 정상적으로 작동하면 성공 메시지가 표시됩니다. (경고는 무시해도 됩니다)

![image](https://github.com/user-attachments/assets/ae9ba79a-420d-452e-8747-672abd2e1a91)


### 4. AWS Cloud9 터미널에 다음을 붙여넣고 실행하여 Bedrock 호출을 테스트합니다.

```
python ~/environment/aws-genai-techcamp-2024/completed/test/bedrock_api.py
```

모든 것이 정상적으로 작동하면 아래와 "안녕?! 만가서 반가워" 에 대한 응답이 출력됩니다.

![image](https://github.com/user-attachments/assets/695a73d2-8cd1-4cc7-b360-fc0af299e02c)

