---
name: wechat-publisher
description: >
  Convert Markdown or Word documents into WeChat Official Account (微信公众号)
  compatible HTML that can be copy-pasted directly into the WeChat editor.
  Applies inline CSS styling with a selectable theme, sanitizes forbidden HTML,
  and adds professional touches: callout boxes, auto table of contents,
  article metadata, copyright footer, and Chinese-English typography spacing.
  Use whenever the user says "convert to WeChat", "公众号文章", "微信公众号格式",
  "转换成公众号", "公众号排版", "make WeChat article", "generate WeChat HTML",
  or provides a .md / .docx file and asks to format it for WeChat publishing.
  Also trigger when the user mentions publishing an article to WeChat Official
  Account or wants a themed / styled article for the WeChat editor.
---

# WeChat Publisher — Markdown / Word → 公众号 HTML（WangChunYan 定制版）

## Purpose

把 Markdown（.md）或 Word（.docx）文档转换成**可直接粘贴进公众号编辑器**的 HTML。
它像一台"公众号打印机"：你给它内容，它还你一篇排版精美、能扛住公众号严苛编辑规则的 HTML。

相比 starter kit，本版本新增了主题系统、callout 框、自动目录、文章元数据、页脚版权、
中文排版优化、本地图片内嵌、多格式输出与文章模板，真正做到「一条命令，成品文章」。

## Quick Start

```bash
# 安装依赖（首次运行会自动装，也可手动）
pip install markdown beautifulsoup4 python-docx lxml

# 基础转换
python scripts/convert_to_wechat.py 我的文章.md 输出.html

# 指定主题 + 全格式输出
python scripts/convert_to_wechat.py 我的文章.md 输出.html --theme accent --formats all

# 从模板新建一篇文章
python scripts/convert_to_wechat.py --new tutorial 新文章.md --author WangChunYan
```

然后：浏览器打开 `输出.html` → Ctrl+A → Ctrl+C → 公众号编辑器（mp.weixin.qq.com）→ Ctrl+V。

## Supported Input Formats

| 格式 | 处理方式 |
|------|----------|
| Markdown (.md) | 支持 front-matter 元数据、表格、围栏代码、callout、脚注 |
| Word (.docx) | 用 python-docx 提取，保留标题层级与加粗/斜体 |
| HTML (.html) | 已有 HTML，直接消毒 + 重新套用主题样式 |

## 输入约定（front-matter 元数据）

Markdown 文件头部可写 YAML 风格的元数据（可选，全部可省略）：

```markdown
---
title: 我的文章标题
author: WangChunYan
date: 2026-07-17
abstract: 一句话摘要，显示在正文顶部
theme: accent
copyright: © 2026 WangChunYan，转载需授权
---
```

## Callout 框语法

在正文中用引用块写，支持 GitHub 风格或表情快捷写法（四选一）：

```markdown
> [!NOTE] 什么是技能包？
> 一句话解释：技能包 = 打包好的能力，装了就可用。

> [!TIP] 小技巧
> 先用 `--list-themes` 看看有哪些主题。

> [!WARNING] 注意
> SVG 图片在公众号保存时会消失，请用 PNG。

> [!PRACTICE] 动手试试
> 运行一条命令，转换你自己的文章。
```

表情快捷写法等价：`> 📘 ...`（知识）、`> 💡 ...`（提示）、`> ⚠️ ...`（注意）、`> 🔧 ...`（实践）。

## 主题系统

`--theme` 一键切换整篇配色，无需改代码：

| 主题 | 说明 |
|------|------|
| `default` | 中性灰，稳重大方（默认） |
| `accent` | 科技蓝，突出强调 |
| `minimal` | 黑白灰，极简 |
| `warm` | 落日橙，温暖 |
| `forest` | 墨绿，自然 |

## 完整能力清单

| 能力 | 状态 | 说明 |
|------|------|------|
| Markdown/Word/HTML 读取 | ✅ | markdown + python-docx |
| 多主题配色 | ✅ 新增 | 5 套主题，`--theme` 切换 |
| Callout 框 | ✅ 新增 | 📘知识/🔧实践/⚠️注意/💡提示 |
| 自动目录 | ✅ 新增 | 从 h2/h3 自动生成，`--no-toc` 关闭 |
| 文章元数据 | ✅ 新增 | 标题/作者/日期/摘要，front-matter |
| 页脚版权声明 | ✅ 新增 | 自动追加，`--no-footer` 关闭 |
| 中文排版优化 | ✅ 新增 | 中英文自动空格（字母边界） |
| 本地图片内嵌 | ✅ 新增 | PNG/JPG → base64，`--embed-images` |
| 多格式输出 | ✅ 新增 | 公众号 HTML + 知乎 Markdown + 纯文本 |
| 文章模板 | ✅ 新增 | 技术教程/学习心得/复盘总结/产品介绍 |
| HTML 标签过滤 | ✅ 保留 | 移除 script/style/iframe/h1/div 等 |
| Inline CSS | ✅ 保留 | 全部内联，无 class/id |

## WeChat HTML Restrictions（自动强制）

- 允许标签：`p, h2, h3, ul, ol, li, span, img, a, table, tr, th, td, br`
- `<h1>` → `<h2>`；`<div>` → `<p>`；`<script>/<style>/<iframe>/<svg>` 移除
- CSS 仅 inline；class/id/on* 属性移除
- 图片：本地 PNG/JPG 可 base64 内嵌；SVG 会丢失需转 PNG

详见 `references/wechat_restrictions.md`。

## 工作流（转换管线）

```
读源文件 → 消毒 → 头部/目录 → 套主题样式 → 清属性 → 中文排版 → 内嵌图片 → 页脚 → 输出
```

## 发布流程（SOP）

1. 用 Markdown 写内容（可 `--new` 从模板起稿）
2. `python scripts/convert_to_wechat.py 文章.md 输出.html --theme accent`
3. 浏览器打开 `输出.html` 预览
4. Ctrl+A → Ctrl+C
5. 公众号编辑器（mp.weixin.qq.com）→ 新建图文 → Ctrl+V
6. 图片按需上传素材库；手机预览 → 调整 → 发布

## 边界情况处理

| 情况 | 处理 |
|------|------|
| 空文件 | 报错，不生成空 HTML |
| 超长文章（>2 万字） | 正常转换，提示公众号字数上限 |
| 非 UTF-8 编码 | 自动回退 GBK |
| 缺依赖 | 首次运行自动 pip 安装 |
| 外部图片 URL | 保留并提示上传素材库 |
| SVG 图片 | 跳过并提示（公众号会丢失） |
| 本地图片 | `--embed-images` 内嵌 base64 |
| 超宽表格 | 建议拆分；本版本不自动加横向滚动 |

## 测试 / 评估

```bash
# 跑通示例
python scripts/convert_to_wechat.py examples/sample_article.md _preview.html --formats all

# 断言检查（无禁用标签、callout/目录/页脚都在）
python tests/test_converter.py
```
