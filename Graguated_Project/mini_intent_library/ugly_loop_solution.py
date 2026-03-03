# -*- coding: utf-8 -*-
"""
故意寫得有點醜的迴圈解 - 用來測試意圖庫能否正確匹配到「解法 B」
"""

UGLY_LOOP = '''
def fib_ugly(n):
    # 算費氏 用迴圈
    x=0
    y=1
    if n==0: return 0
    if n==1: return 1
    i=2
    while i<=n:
        t=x+y
        x=y
        y=t
        i=i+1
    return y
'''
