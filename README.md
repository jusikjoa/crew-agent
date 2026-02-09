# Crew AI Agent

LangChain을 사용한 AI Agent 서비스

## 특징

- **GPT-4 기반 AI Agent**: OpenAI의 최신 모델을 활용한 지능형 에이전트
- **자동 도구 선택**: 질문에 따라 필요한 도구를 자동으로 선택하고 실행
- **웹 검색**: DuckDuckGo를 통한 실시간 정보 검색 (API 키 불필요)
- **API 호출**: 외부 REST API 통합 및 데이터 수집
- **대화형 인터페이스**: CLI를 통한 실시간 상호작용
- **Python 3.13 호환**: 최신 Python 버전 지원

## 프로젝트 구조

```
crew-agent/
├── src/
│   ├── agent.py              # AI Agent 핵심 구현
│   ├── main.py               # 대화형 CLI 진입점
│   ├── __init__.py
│   └── tools/                # 커스텀 도구 모듈
│       ├── __init__.py
│       ├── web_search.py     # 웹 검색 도구
│       └── api_caller.py     # API 호출 도구
├── examples/
│   └── basic_usage.py        # 사용 예제 모음
├── test_agent.py             # 빠른 테스트 스크립트
├── requirements.txt          # Python 패키지 의존성
├── .env.example             # 환경 변수 템플릿
├── .env                     # 실제 환경 변수 (생성 필요)
└── README.md                # 프로젝트 문서
```

## 빠른 시작

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 OpenAI API 키를 설정하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Agent 테스트

```bash
python test_agent.py
```

## 설치 (상세)

### 가상 환경 사용 (권장)

```bash
# 가상 환경 생성
python -m venv venv

# 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 요구사항

- Python 3.9 이상 (Python 3.13 테스트 완료)
- OpenAI API 키 (필수)

## 사용 방법

### 1. 빠른 테스트

```bash
python test_agent.py
```

### 2. 대화형 모드

```bash
cd src
python main.py
```

대화형 모드에서는 Agent와 자유롭게 대화할 수 있습니다. 종료하려면 `quit` 또는 `exit`을 입력하세요.

### 3. Python 코드에서 사용

```python
import sys
sys.path.insert(0, 'src')

from agent import create_agent

# Agent 생성
agent = create_agent(
    model_name="gpt-4",      # 사용할 모델
    temperature=0.7,         # 생성 온도 (0~1)
    verbose=False            # 상세 로그 출력 여부
)

# 간단한 질문
response = agent.run("Hello! What can you help me with?")
print(response)

# Agent가 자동으로 도구를 선택하는 예시
response = agent.run("What's the weather like today?")
print(response)
```

### 4. 예제 실행

```bash
cd examples
python basic_usage.py
```

## 주요 컴포넌트

### 1. CrewAgent 클래스

AI Agent의 핵심 클래스로, LangChain의 Tool Calling 기능을 활용합니다.

```python
import sys
sys.path.insert(0, 'src')
from agent import CrewAgent

# Agent 생성
agent = CrewAgent(
    model_name="gpt-4",      # OpenAI 모델: gpt-4, gpt-4-turbo, gpt-3.5-turbo
    temperature=0.7,         # 창의성 수준 (0: 일관적, 1: 창의적)
    verbose=True             # 도구 호출 과정 출력
)

# 질문하기
result = agent.run("Python의 최신 버전은?")
print(result)

# 비동기 실행
result = await agent.arun("질문 내용")
```

**작동 방식:**
1. 사용자 질문 분석
2. 필요한 경우 적절한 도구 자동 선택
3. 도구 실행 및 결과 수집
4. 최종 답변 생성

### 2. 커스텀 도구

Agent가 자동으로 사용할 수 있는 도구들입니다.

#### WebSearchTool

DuckDuckGo를 사용한 실시간 웹 검색 도구 (API 키 불필요)

**기능:**
- 최신 정보 검색
- 상위 5개 결과 반환
- 제목, 설명, 링크 포함

#### APICallerTool

외부 REST API 호출 도구

**지원 메서드:** GET, POST, PUT, DELETE

**사용 예시:**
Agent가 자동으로 이 도구를 사용하여 API를 호출합니다.

```python
# Agent에게 API 호출 요청
response = agent.run("""
Call this API and tell me the result:
URL: https://jsonplaceholder.typicode.com/posts/1
Method: GET
""")
```

## Agent 작동 원리

이 Agent는 LangChain의 **Tool Calling** 방식을 사용합니다:

### 기본 흐름

1. **사용자 질문 입력**
   ```
   "What's the latest version of Python?"
   ```

2. **LLM 분석** (GPT-4)
   - 질문 이해
   - 필요한 도구 판단

3. **도구 호출** (필요시)
   ```
   Tool: web_search
   Input: "Python latest version 2026"
   ```

4. **결과 통합**
   - 도구 실행 결과 수집
   - LLM이 최종 답변 생성

5. **최종 응답**
   ```
   "The latest version of Python is 3.13.2..."
   ```

### 장점

- **자동화**: 필요한 도구를 자동으로 선택
- **유연성**: 복잡한 질문도 여러 도구를 조합하여 해결
- **확장성**: 새로운 도구를 쉽게 추가 가능

## 문제 해결

### ModuleNotFoundError

```bash
# 패키지 재설치
pip install -r requirements.txt
```

### OPENAI_API_KEY not found

1. `.env.example`을 `.env`로 복사했는지 확인
2. `.env` 파일에 실제 API 키 입력
3. 프로젝트 루트 디렉토리에서 실행

### 한글 인코딩 문제 (Windows)

Windows 콘솔에서 한글이 깨지는 것은 정상입니다. Agent의 기능은 정상 작동합니다.

```bash
# UTF-8 인코딩 설정 (선택사항)
chcp 65001
```

### Import 오류

```python
# 올바른 import 방법
import sys
sys.path.insert(0, 'src')
from agent import create_agent
```

## API 키 발급

### OpenAI API (필수)

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. 계정 생성 및 로그인
3. API Keys 메뉴에서 새 키 생성
4. `.env` 파일에 키 추가

**요금**: 사용량 기반 과금 (GPT-4: ~$0.03/1K tokens)

## 개발 가이드

### 새로운 도구 추가하기

도구를 추가하면 Agent가 자동으로 사용할 수 있습니다.

#### 1단계: 도구 클래스 생성

`src/tools/my_tool.py` 파일을 만듭니다:

```python
from typing import Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

class MyCustomTool(BaseTool):
    """도구에 대한 설명 (Agent가 이를 보고 사용 여부 결정)"""

    name: str = "my_custom_tool"
    description: str = (
        "이 도구가 무엇을 하는지 명확하게 설명하세요. "
        "예: '날씨 정보를 조회할 때 사용합니다. 도시 이름을 입력으로 받습니다.'"
    )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """도구 실행 로직"""
        try:
            # 여기에 실제 기능 구현
            result = f"Query received: {query}"
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """비동기 실행 (선택사항)"""
        return self._run(query, run_manager)
```

#### 2단계: 도구 등록

`src/tools/__init__.py`에 추가:

```python
from .my_tool import MyCustomTool

__all__ = ["WebSearchTool", "APICallerTool", "MyCustomTool"]
```

#### 3단계: Agent에 추가

`src/agent.py`의 `_setup_tools()` 메서드 수정:

```python
def _setup_tools(self) -> List[BaseTool]:
    """Setup available tools"""
    tools = [
        WebSearchTool(),
        APICallerTool(),
        MyCustomTool(),  # 새 도구 추가
    ]
    return tools
```

#### 4단계: 테스트

```python
from src.agent import create_agent

agent = create_agent(verbose=True)
response = agent.run("Use my custom tool with input: test")
print(response)
```

### 모델 변경

다른 OpenAI 모델을 사용하려면:

```python
agent = create_agent(
    model_name="gpt-3.5-turbo",  # 더 빠르고 저렴
    # model_name="gpt-4-turbo",   # 더 강력
    # model_name="gpt-4",          # 가장 강력 (기본값)
)
```

### 프롬프트 수정

Agent의 행동을 변경하려면 [src/agent.py:77-82](src/agent.py#L77-L82)의 시스템 메시지를 수정하세요.

## 추가 예제

### API 호출 예제

```python
agent = create_agent(verbose=True)

response = agent.run("""
Please fetch data from this API and summarize it:
https://jsonplaceholder.typicode.com/posts/1
""")
print(response)
```

### 웹 검색 예제

```python
agent = create_agent(verbose=True)

response = agent.run("What are the latest trends in AI for 2026?")
print(response)
```

### 복합 작업 예제

```python
agent = create_agent(verbose=False)

response = agent.run("""
1. Search for the latest Python version
2. Then check if there's an API that provides Python release information
3. Summarize your findings
""")
print(response)
```

## 기술 스택

- **LangChain**: AI Agent 프레임워크
- **OpenAI GPT-4**: 대형 언어 모델
- **Python 3.9+**: 프로그래밍 언어
- **DuckDuckGo**: 웹 검색 (API 키 불필요)
- **Requests**: HTTP 클라이언트

## 참고 자료

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LangChain Tools Guide](https://python.langchain.com/docs/modules/agents/tools/)

## 라이선스

MIT License

---

**Made with LangChain and GPT-4**
