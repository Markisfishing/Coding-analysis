# 迷你意圖庫 (計畫 4.2)

用「一題」費氏數列做實驗：三種正確解法 (A 遞迴、B 迴圈、C 公式) 經 GraphCodeBERT 轉成向量存入 Qdrant，再以「故意寫醜的迴圈解」查詢，驗證能正確匹配到解法 B。

## 1. 啟動 Qdrant

```bash
cd mini_intent_library
docker compose up -d
```

確認：<http://localhost:6333/dashboard> 可開即表示 Qdrant 已啟動。

## 2. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

（建議在專案虛擬環境中執行。）

## 3. 執行腳本

```bash
python embed_and_search.py
```

腳本會：

- 從 Hugging Face 載入 `microsoft/graphcodebert-base`
- 將三種標準解法轉成 768 維向量並寫入 Qdrant
- 將「醜迴圈解」轉成向量後在 Qdrant 搜尋
- 印出相似度排序，預期第一名為 **B_loop（迴圈解）**

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `fibonacci_solutions.py` | 三種標準解法：A 遞迴、B 迴圈、C 公式 |
| `ugly_loop_solution.py` | 故意寫醜的迴圈解，用來測試匹配 |
| `embed_and_search.py` | 主程式：embedding + 寫入 Qdrant + 查詢 |
| `docker-compose.yml` | 本機 Qdrant 容器設定 |

## 停止 Qdrant

```bash
docker compose down
```
