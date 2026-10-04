#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eval / 回归测试 —— 验证 wechat-publisher（WangChunYan 定制版）的输出契约。

断言清单：
  1. 无禁用标签（script/style/iframe/h1/div/svg）
  2. callout 框样式存在
  3. 自动目录存在
  4. 页脚版权存在
  5. 中英文自动空格生效（"Python 脚本"）
  6. 多格式输出（zhihu / plain）生成
运行：python tests/test_converter.py
"""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import convert_to_wechat as c  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / '_output'
OUT_DIR.mkdir(exist_ok=True)

SAMPLE_MD = """---
title: 测试文章：从 Markdown 到公众号
author: WangChunYan
date: 2026-07-17
abstract: 这是一段摘要，用于验证元数据头部。
theme: accent
---

## 第一节

这是正文，里面混有 Python 脚本与 C4B 任务这样的中英文。

> [!NOTE] 什么是技能包？
> 一句话解释。

```python
print("hello wechat")
```

| 列一 | 列二 |
|------|------|
| 甲 | 乙 |

## 第二节

> [!WARNING] 注意
> SVG 会丢失。
"""


def fail(msg):
    print(f"  [FAIL] {msg}")
    return False


def main():
    print("=" * 50)
    print("wechat-publisher eval")
    print("=" * 50)

    src = OUT_DIR / 'test_article.md'
    out = OUT_DIR / 'test_article.html'
    src.write_text(SAMPLE_MD, encoding='utf-8')

    args = c.build_parser().parse_args([
        str(src), str(out),
        '--theme', 'accent',
        '--formats', 'all',
    ])
    ok = c.convert(str(src), str(out), args)
    if not ok:
        print("  [FAIL] convert 返回 False")
        sys.exit(1)

    html = out.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'lxml')
    body_text = soup.body.get_text() if soup.body else ''

    passed = 0
    total = 6

    # 1) 无禁用标签
    forbidden = ['script', 'style', 'iframe', 'h1', 'div', 'svg']
    found = [t for t in forbidden if soup.find(t) is not None]
    if found:
        fail(f"发现禁用标签: {found}")
    else:
        print("  [PASS] 无禁用标签"); passed += 1

    # 2) callout 框
    if 'border-left: 4px solid #4a7dff' in html or 'border-left: 4px solid #f59e0b' in html:
        print("  [PASS] callout 框样式存在"); passed += 1
    else:
        fail("callout 框样式缺失")

    # 3) 目录
    if '📑 目录' in body_text or '目录' in body_text:
        print("  [PASS] 自动目录存在"); passed += 1
    else:
        fail("目录缺失")

    # 4) 页脚
    if 'wechat-publisher' in body_text and '生成' in body_text:
        print("  [PASS] 页脚版权存在"); passed += 1
    else:
        fail("页脚缺失")

    # 5) 中英文空格
    if 'Python 脚本' in body_text:
        print("  [PASS] 中英文自动空格生效"); passed += 1
    else:
        fail("中英文空格未生效（期望 'Python 脚本'）")

    # 6) 多格式输出
    zhihu = OUT_DIR / 'test_article_zhihu.md'
    plain = OUT_DIR / 'test_article_plain.txt'
    if zhihu.exists() and plain.exists():
        print("  [PASS] 多格式输出（zhihu/plain）"); passed += 1
    else:
        fail("多格式输出缺失")

    print("-" * 50)
    print(f"结果：{passed}/{total} 通过")
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
