# -*- coding: utf-8 -*-
"""
意圖庫服務：供後端 API 呼叫。給定程式碼字串，回傳與 Qdrant 內標準解的相似度匹配結果。
使用 lazy loading，第一次呼叫時才載入 GraphCodeBERT。
"""
from typing import List, Optional, Any

# 設定（與 embed_and_search 一致）
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
DEFAULT_COLLECTION = "fibonacci_intents"
MODEL_NAME = "microsoft/graphcodebert-base"
EMBED_DIM = 768

# 全域快取，第一次呼叫時載入
_model = None
_tokenizer = None
_device = None


def _load_model() -> None:
    global _model, _tokenizer, _device
    if _model is not None:
        return
    import torch
    from transformers import AutoTokenizer, AutoModel
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    _model = AutoModel.from_pretrained(MODEL_NAME).to(_device)
    _model.eval()


def get_embedding(code: str) -> List[float]:
    """將程式碼轉成 768 維向量（mean pooling）。會 lazy load 模型。"""
    import torch
    _load_model()
    inputs = _tokenizer(
        code,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    ).to(_device)
    with torch.no_grad():
        outputs = _model(**inputs)
    last_hidden = outputs.last_hidden_state
    attention = inputs["attention_mask"]
    mask = attention.unsqueeze(-1).expand(last_hidden.size()).float()
    sum_emb = torch.sum(last_hidden * mask, dim=1)
    sum_mask = torch.clamp(mask.sum(dim=1), min=1e-9)
    embedding = (sum_emb / sum_mask).squeeze(0).cpu().tolist()
    return embedding


def get_intent_match(
    code: str,
    collection_name: str = DEFAULT_COLLECTION,
    limit: int = 3,
) -> Optional[dict[str, Any]]:
    """
    查詢與程式碼最相似的標準解法。
    回傳格式：{
        "best_match": { "solution_id": "B_loop", "description": "迴圈解", "score": 0.96 },
        "all_matches": [ { "solution_id", "description", "score" }, ... ]
    }
    若 Qdrant 連線失敗或 collection 不存在，回傳 None。
    """
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        return None
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    except Exception:
        return None
    try:
        query_vec = get_embedding(code)
        response = client.query_points(
            collection_name=collection_name,
            query=query_vec,
            limit=limit,
        )
        points = response.points
    except Exception:
        return None
    if not points:
        return None
    all_matches = [
        {
            "solution_id": p.payload.get("solution_id", ""),
            "description": p.payload.get("description", ""),
            "score": round(float(p.score), 4),
        }
        for p in points
    ]
    best = all_matches[0] if all_matches else None
    return {
        "best_match": best,
        "all_matches": all_matches,
    }
