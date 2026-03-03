# 目前可測試項目與步驟

以下都是**現有程式**可以立刻測的，不需等整合。

---

## 快速指令一覽

| 想做什麼 | 指令 |
|----------|------|
| 建沙盒映像 | `cd code_sandbox && docker build -t python-sandbox .` |
| 啟動後端 | `uvicorn code_sandbox.main:app --reload --host 127.0.0.1 --port 8000` |
| 啟動 Qdrant | `cd mini_intent_library && docker compose up -d` |
| 跑意圖庫腳本 | `python mini_intent_library/embed_and_search.py` |
| 用 API 送程式碼 | `curl -X POST http://127.0.0.1:8000/submit_code -H "Content-Type: application/json" -d "{\"code\": \"print(1+1)\"}"` |

（以上請在專案根目錄、且已 `activate` 虛擬環境下執行；啟動後端與跑意圖庫可開兩個終端分別執行。）

---

## 前置：環境確認

- 已安裝：Python 3、Docker、專案虛擬環境 (`.venv`)
- 依賴已裝：`code_sandbox` 用 FastAPI；`mini_intent_library` 用 `requirements.txt`（transformers, torch, qdrant-client）

---

## 測試 1：Docker 沙盒執行（code_sandbox）

**目的**：確認「在 Docker 裡執行程式碼」這一段正常。

### 步驟

1. **建沙盒映像**（若還沒建過）：
   ```bash
   cd c:\Graguated_Project\code_sandbox
   docker build -t python-sandbox .
   ```

2. **啟動 FastAPI**：
   ```bash
   cd c:\Graguated_Project
   .\.venv\Scripts\activate
   uvicorn code_sandbox.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **方式 A：用網頁**
   - 用瀏覽器開啟 `code_sandbox/index.html`（或透過簡單 HTTP server 開）。
   - 在文字框輸入 Python 程式碼，按「送出執行」。
   - 預期：看到執行結果或錯誤訊息。

4. **方式 B：用 curl**
   ```bash
   curl -X POST http://127.0.0.1:8000/submit_code -H "Content-Type: application/json" -d "{\"code\": \"print(1+1)\"}"
   ```
   - 預期：JSON 裡有 `stdout`、`stderr`、`returncode`；例如 `stdout` 為 `2`。

5. **可順便觀察**
   - 故意送有語法錯誤的程式碼（例如 `print(1`），看 `stderr` 是否有 Python 錯誤訊息（等同「執行時語法錯誤」）。
   - 送 `while True: pass` 等，看是否約 5 秒後回傳逾時錯誤。

---

## 測試 2：意圖庫（GraphCodeBERT + Qdrant）

**目的**：確認「程式碼 → 向量 → Qdrant 查詢 → 得到最相似解法」整段可跑。

### 步驟

1. **啟動 Qdrant**：
   ```bash
   cd c:\Graguated_Project\mini_intent_library
   docker compose up -d
   ```
   - 可開 http://localhost:6333/dashboard 確認 Qdrant 有起來。

2. **執行意圖庫腳本**（會下載 GraphCodeBERT，第一次較久）：
   ```bash
   cd c:\Graguated_Project
   .\.venv\Scripts\activate
   python mini_intent_library/embed_and_search.py
   ```
   - 預期輸出包含：
     - 已寫入 3 筆標準解法 (A, B, C)
     - 查詢「醜迴圈解」的相似度排序：第 1 名應為 **B_loop (迴圈解)**
     - 最後一行：`[OK] 成功：與「解法 B（迴圈解）」相似度最高...`

3. **若只改查詢程式碼**
   - 可改 `ugly_loop_solution.py` 裡的 `UGLY_LOOP` 字串，再跑一次 `embed_and_search.py`，看排名是否合理（例如改成遞迴風格的程式碼，看是否較接近 A）。

---

## 測試 3：整合 API（同一請求：執行 ＋ 意圖庫）

**前提**：Qdrant 已啟動且已建檔（跑過一次 **測試 2** 的 `embed_and_search.py`）。

1. 啟動後端：`uvicorn code_sandbox.main:app --reload --host 127.0.0.1 --port 8000`（在專案根目錄、已啟用虛擬環境）。
2. 用瀏覽器開 `code_sandbox/index.html`，或 curl：
   ```bash
   curl -X POST http://127.0.0.1:8000/submit_code -H "Content-Type: application/json" -d "{\"code\": \"def fib(n):\\n    a,b=0,1\\n    for i in range(n): a,b=b,a+b\\n    return a\"}"
   ```
3. 回傳應包含 `stdout`、`stderr`、`returncode` 以及 **`intent_match`**：`best_match` 為最相似解法（例如 B_loop）、`all_matches` 為前幾名。若 Qdrant 未開或未建檔，`intent_match` 會是 `null`。
4. 網頁上執行結果下方會顯示「意圖庫匹配」區塊（最相似解法與相似度）。

---

## 尚未能測試的部分（等實作後再測）

- **測資比對**：目前沒有題目測資與比對邏輯。
- **xAPI**：沒有產生 xAPI Statement 的程式。
- **KGNN-KT**：沒有知識圖或 KT 分析。
- **LLM 引導**：沒有呼叫 LLM 的程式。

這些可在 `PROJECT_STATUS.md` 的整合規劃裡，以「預留介面」方式先接，之後再補實作與測試。
