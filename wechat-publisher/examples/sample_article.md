---
title: 示例文章：用一个技能包放大你的能力
author: 你的名字
date: 2026-07-17
abstract: 这是一篇示例，展示 wechat-publisher 的主题、目录、callout 框、代码块、表格与页脚等全部能力。
theme: warm
---

## 为什么要做技能包

在 AI 时代，**个人能力的价值不在于你自己用了多少次，而在于能被复制多少次**。

一个技能被 10 人用 = 放大 10 倍价值；被 100 人用 = 放大 100 倍。

> [!NOTE] 什么是技能包
> 技能包 = 打包好的能力，别人安装后即可直接运行，零信息损耗。

## 它长什么样

### 目录自动生成

本文开头的目录就是自动生成的，不需要你手动维护。

### callout 框

> [!TIP] 小技巧
> 用 `> [!TIP]` 开头，就能得到一个提示框。

> [!WARNING] 注意
> 公众号保存时 SVG 会消失，图片请用 PNG。

### 代码与表格

```python
def hello():
    print("hello, wechat")
```

| 能力 | 状态 |
|------|------|
| 主题 | ✅ |
| 目录 | ✅ |
| 页脚 | ✅ |

## 怎么用

```bash
python scripts/convert_to_wechat.py examples/sample_article.md 输出.html --theme warm
```

然后浏览器打开、全选复制、粘贴进公众号编辑器即可。

---

*本文由 wechat-publisher 生成。*
