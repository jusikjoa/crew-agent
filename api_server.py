"""
AI Agent 대화 API 서버 (비동기 방식)
"""
import uuid
import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.agent import CrewAgent

app = FastAPI(title="AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에이전트 인스턴스
agent = CrewAgent(verbose=True)

# 작업 저장소: {task_id: {"status": ..., "reply": ...}}
tasks = {}


class ChatRequest(BaseModel):
    message: str


class TaskCreatedResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "pending" | "done" | "error"
    reply: Optional[str] = None


def _run_agent(task_id: str, message: str):
    """백그라운드에서 에이전트 실행"""
    try:
        reply = agent.run(message)
        tasks[task_id] = {"status": "done", "reply": reply}
    except Exception as e:
        tasks[task_id] = {"status": "error", "reply": f"오류: {str(e)}"}


@app.get("/")
def root():
    return {
        "service": "AI Agent API",
        "endpoints": {
            "POST /chat": "에이전트에게 메시지 전송 → task_id 반환",
            "GET /chat/{task_id}": "작업 결과 조회",
            "POST /clear": "대화 히스토리 초기화",
        }
    }


@app.post("/chat", response_model=TaskCreatedResponse)
def chat(req: ChatRequest):
    """
    에이전트에게 메시지를 보냅니다.
    즉시 task_id를 반환하고, 에이전트는 백그라운드에서 실행됩니다.
    결과는 GET /chat/{task_id}로 조회하세요.
    """
    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {"status": "pending", "reply": None}

    thread = threading.Thread(target=_run_agent, args=(task_id, req.message))
    thread.start()

    return TaskCreatedResponse(task_id=task_id, status="pending")


@app.get("/chat/{task_id}", response_model=TaskStatusResponse)
def get_result(task_id: str):
    """작업 결과를 조회합니다."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="존재하지 않는 task_id입니다.")

    task = tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        reply=task["reply"],
    )


@app.post("/clear")
def clear():
    """대화 히스토리를 초기화합니다."""
    agent.clear_history()
    return {"message": "대화 히스토리가 초기화되었습니다."}


if __name__ == "__main__":
    print("=" * 50)
    print("AI Agent API 서버")
    print("=" * 50)
    print("API 문서: http://localhost:8000/docs")
    print()
    print("사용법:")
    print("  1) POST /chat {message} → task_id 반환")
    print("  2) GET /chat/{task_id}  → 결과 조회")
    print("  3) POST /clear          → 히스토리 초기화")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8000)
