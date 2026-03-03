from pathlib import Path
import sys

# 專案根目錄加入 path，才能 import mini_intent_library
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess

app = FastAPI()

# 設定 CORS，這樣之後用本機的 HTML 檔測試時才不會被瀏覽器阻擋
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義前端傳過來的資料格式
class CodeRequest(BaseModel):
    code: str

def _get_intent_match(code: str):
    """呼叫迷你意圖庫，取得最相似解法。失敗時回傳 None。"""
    try:
        from mini_intent_library.intent_service import get_intent_match
        return get_intent_match(code, limit=3)
    except Exception:
        return None


@app.post("/submit_code")
def submit_code(request: CodeRequest):
    try:
        # 1. Docker 執行程式碼
        process = subprocess.run(
            [
                "docker", "run", "--rm", "-i",
                "--network", "none",
                "--memory", "128m",
                "--cpus", "0.5",
                "python-sandbox",
                "python", "-"
            ],
            input=request.code,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=5,
        )
        result = {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "returncode": process.returncode,
        }

        # 2. 意圖庫：GraphCodeBERT + Qdrant 取得最相似解法
        intent_match = _get_intent_match(request.code)
        result["intent_match"] = intent_match

        # 3. 預留：之後可在此接 xAPI、KGNN-KT、LLM 引導
        # result["xapi_statement"] = ...
        # result["kt_analysis"] = ...
        # result["llm_guide"] = ...

        return result

    except subprocess.TimeoutExpired:
        return {"error": "執行失敗：程式執行時間過長 (超過 5 秒)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))