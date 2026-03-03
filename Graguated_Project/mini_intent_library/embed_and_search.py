# -*- coding: utf-8 -*-
"""
迷你意圖庫 (4.2)：用 GraphCodeBERT 將費氏數列解法轉成向量，存進 Qdrant，
並用「醜迴圈解」查詢，驗證能正確匹配到解法 B（迴圈解）。
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from fibonacci_solutions import STANDARD_SOLUTIONS
from ugly_loop_solution import UGLY_LOOP
from intent_service import get_embedding, EMBED_DIM, QDRANT_HOST, QDRANT_PORT, DEFAULT_COLLECTION

COLLECTION_NAME = DEFAULT_COLLECTION


def main():
    # 連線 Qdrant（請先 docker compose up -d）
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # 若 collection 已存在可刪除重建，方便重跑
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

    # 將 3 個標準解法轉成向量並寫入 Qdrant（get_embedding 會 lazy load 模型）
    points = []
    for idx, (sid, code, desc) in enumerate(STANDARD_SOLUTIONS):
        vec = get_embedding(code.strip())
        points.append(
            PointStruct(
                id=idx,
                vector=vec,
                payload={"solution_id": sid, "description": desc, "code_preview": code.strip()[:80] + "..."},
            )
        )
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"已寫入 {len(points)} 筆標準解法 (A, B, C)。")

    # 將「醜迴圈解」轉成向量並搜尋
    query_vec = get_embedding(UGLY_LOOP.strip())
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=3,
    )
    results = response.points

    # 輸出結果：預期第一名是 B_loop
    print("\n--- 查詢「醜迴圈解」的相似度排序 ---")
    for rank, hit in enumerate(results, 1):
        pid = hit.payload.get("solution_id", "?")
        desc = hit.payload.get("description", "?")
        score = hit.score
        print(f"  第 {rank} 名: {pid} ({desc}) — 相似度: {score:.4f}")

    top = results[0]
    if top.payload.get("solution_id") == "B_loop":
        print("\n[OK] 成功：與「解法 B（迴圈解）」相似度最高，迷你意圖庫運作正常。")
    else:
        print(f"\n[FAIL] 預期第一名為 B_loop，實際為 {top.payload.get('solution_id')}。")


if __name__ == "__main__":
    main()
