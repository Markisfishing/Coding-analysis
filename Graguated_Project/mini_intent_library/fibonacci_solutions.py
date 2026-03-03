# -*- coding: utf-8 -*-
"""
費氏數列 - 三種標準解法（供迷你意圖庫 4.2 使用）
"""

# ========== 解法 A：遞迴解 ==========
FIB_RECURSIVE = '''
def fib_recursive(n):
    """費氏數列 - 遞迴解"""
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)
'''

# ========== 解法 B：迴圈解 ==========
FIB_LOOP = '''
def fib_loop(n):
    """費氏數列 - 迴圈解 (迭代)"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
'''

# ========== 解法 C：公式解 (Binet formula) ==========
FIB_FORMULA = '''
import math

def fib_formula(n):
    """費氏數列 - Binet 公式解"""
    if n <= 1:
        return n
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    return int((phi ** n - psi ** n) / math.sqrt(5))
'''

# 供腳本使用的標準解法清單
STANDARD_SOLUTIONS = [
    ("A_recursive", FIB_RECURSIVE, "遞迴解"),
    ("B_loop", FIB_LOOP, "迴圈解"),
    ("C_formula", FIB_FORMULA, "公式解"),
]
