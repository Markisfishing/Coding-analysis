# 專案整體流程與進度

目標流程：

```
Docker 執行 → 檢查語法 → 比對測資 → GraphCodeBERT → V_student
    → Qdrant 拉出 V_A, V_B 算相似度 → xAPI Statement → KGNN-KT 分析 → LLM 引導對話
```

---

## 各階段進度

| 階段 | 說明 | 狀態 | 位置 / 備註 |
|------|------|------|-------------|
| **1. Docker 執行** | 在容器內執行程式碼 | ✅ 已完成 | `code_sandbox/`：FastAPI + Docker 跑 Python |
| **2. 檢查語法** | 執行前或執行時語法錯誤偵測 | ⚠️ 部分 | 目前僅靠執行後 `stderr` 判斷，無獨立「純語法檢查」 |
| **3. 比對測資** | 用題目的 input/output 測資判對錯 | ❌ 未實作 | 需題目測資格式 + 跑碼比對邏輯 |
| **4. GraphCodeBERT → V_student** | 把學生程式碼轉成向量 | ✅ 已有能力 | `mini_intent_library/embed_and_search.py` 的 `get_embedding()`，目前為獨立腳本 |
| **5. Qdrant 拉 V_A, V_B 算相似度** | 取該題標準解向量、算與 V_student 相似度 | ✅ 已完成 | 同上，用 `query_points` 搜尋，回傳最相似解法 (如 B_loop) |
| **6. xAPI Statement** | 把答題行為整理成 xAPI 語句 | ❌ 未實作 | 需定義 verb/activity/result 等結構 |
| **7. KGNN-KT 分析** | 知識追蹤 / 答題狀況分析 | ❌ 未實作 | 需知識圖、題目-知識點、KT 模型或規則 |
| **8. LLM 引導對話** | 依 Prompt 生成引導回覆 | ❌ 未實作 | 需串接 LLM API 與 Prompt 設計 |

---

## 整合狀態（後端）

**已完成：** 同一請求內「Docker 執行 ＋ 意圖庫」已串接。

- **code_sandbox**：`/submit_code` 會先執行 Docker，再呼叫 **mini_intent_library** 的 `get_intent_match(code)`，回傳中多了 `intent_match`（含 `best_match`、`all_matches`）。意圖庫邏輯維持在 **mini_intent_library**（`intent_service.py`），由 code_sandbox 透過 `sys.path` 匯入呼叫。
- **xAPI / KGNN-KT / LLM**：在 `main.py` 已預留註解，之後實作可接在同一支 API 回傳裡。

---

## 目錄結構（與流程對應）

```
Graguated_Project/
├── code_sandbox/          # Docker 執行 + 前端測試
│   ├── main.py            # FastAPI：/submit_code 執行程式碼
│   ├── index.html         # 簡單測試頁
│   └── Dockerfile         # 沙盒映像
├── mini_intent_library/   # 意圖庫：GraphCodeBERT + Qdrant（被 code_sandbox 呼叫）
│   ├── intent_service.py  # 供 API 呼叫：get_intent_match(code)
│   ├── embed_and_search.py  # 建檔/示範腳本（寫入 Qdrant + 查詢驗證）
│   ├── fibonacci_solutions.py
│   ├── ugly_loop_solution.py
│   ├── docker-compose.yml
│   └── requirements.txt
├── PROJECT_STATUS.md      # 本檔案：流程與進度
└── TESTING_GUIDE.md       # 目前可測試項目與步驟
```

未來的模組可能放在例如：`xapi/`、`kgnn_kt/`、`llm_guide/`，再由同一後端依序呼叫。
