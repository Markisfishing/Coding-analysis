# 使用輕量級的 Python 映像檔
FROM python:3.10-slim

# 建立一個非 root 使用者，增加安全性，避免惡意程式碼擁有最高權限
RUN useradd -m sandboxuser
USER sandboxuser

# 設定工作目錄
WORKDIR /app