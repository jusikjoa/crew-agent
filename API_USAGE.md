# AI Agent API

## 설치 및 실행

```bash
pip install -r requirements.txt
python api_server.py
```

서버: `http://localhost:8000`
API 문서(Swagger UI): `http://localhost:8000/docs`

---

## 엔드포인트

### 1. `POST /chat` — 메시지 전송

에이전트에게 메시지를 보냅니다. 즉시 `task_id`를 반환하고, 에이전트는 백그라운드에서 실행됩니다.

**Request**
```json
{
  "message": "오늘 날씨 어때?"
}
```

**Response** `200`
```json
{
  "task_id": "a1b2c3d4",
  "status": "pending"
}
```

**예시**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "오늘 날씨 어때?"}'
```

---

### 2. `GET /chat/{task_id}` — 결과 조회

작업 상태와 결과를 조회합니다. `status`가 `done`이 될 때까지 폴링하세요.

**Response** `200`

진행 중:
```json
{
  "task_id": "a1b2c3d4",
  "status": "pending",
  "reply": null
}
```

완료:
```json
{
  "task_id": "a1b2c3d4",
  "status": "done",
  "reply": "오늘 서울 날씨는..."
}
```

오류:
```json
{
  "task_id": "a1b2c3d4",
  "status": "error",
  "reply": "오류: ..."
}
```

**Response** `404` — 존재하지 않는 task_id

**예시**
```bash
curl http://localhost:8000/chat/a1b2c3d4
```

---

### 3. `POST /clear` — 대화 히스토리 초기화

에이전트의 대화 히스토리를 초기화합니다.

**Response** `200`
```json
{
  "message": "대화 히스토리가 초기화되었습니다."
}
```

**예시**
```bash
curl -X POST http://localhost:8000/clear
```

---

## 사용 예시

### Python

```python
import requests
import time

# 1) 메시지 전송
res = requests.post("http://localhost:8000/chat", json={"message": "졸업시뮬레이션 돌려줘"})
task_id = res.json()["task_id"]
print(f"task_id: {task_id}")

# 2) 결과 폴링
while True:
    res = requests.get(f"http://localhost:8000/chat/{task_id}")
    data = res.json()
    if data["status"] != "pending":
        print(data["reply"])
        break
    print("처리 중...")
    time.sleep(3)
```

### JavaScript (fetch)

```javascript
// 1) 메시지 전송
const res = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: '졸업시뮬레이션 돌려줘'})
});
const {task_id} = await res.json();

// 2) 결과 폴링
const poll = setInterval(async () => {
  const res = await fetch(`http://localhost:8000/chat/${task_id}`);
  const data = await res.json();
  if (data.status !== 'pending') {
    clearInterval(poll);
    console.log(data.reply);
  }
}, 3000);
```

---

## status 값

| status | 설명 |
|--------|------|
| `pending` | 에이전트가 처리 중 |
| `done` | 완료, `reply`에 결과 포함 |
| `error` | 오류 발생, `reply`에 오류 메시지 포함 |

---

## 에이전트 기능

| 기능 | 설명 | 예시 메시지 |
|------|------|------------|
| 웹 검색 | DuckDuckGo로 실시간 검색 | "카이스트 졸업요건 알려줘" |
| API 호출 | 외부 REST API 호출 | "이 API에서 데이터 가져와" |
| 졸업시뮬레이션 | KAIST 학사시스템 자동화 | "졸업시뮬레이션 돌려줘" |
| 일반 대화 | 번역, 요약, 코드 작성 등 | "이 문장 영어로 번역해줘" |

## 주의사항

- 졸업시뮬레이션은 브라우저가 열리고 **수동 로그인(2FA)**이 필요합니다
- 대화 히스토리는 서버 메모리에 유지됩니다 (서버 재시작 시 초기화)
- 한 번에 하나의 졸업시뮬레이션만 실행 가능합니다
