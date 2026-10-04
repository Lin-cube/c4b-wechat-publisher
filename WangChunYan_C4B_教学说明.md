# WangChunYan_C4B_教学说明：怎么安装、怎么用这个技能

> 技能名：`wechat-publisher`（WangChunYan 定制版）
> 一句话定义：**输入 Markdown / Word，输出 copy-paste ready 的公众号 HTML。**

---

## 一、这个技能是做什么的

它把一篇 Markdown 或 Word 文档，变成一段能**直接粘贴进公众号编辑器**的 HTML。
粘贴过去之后，标题、正文、代码块、表格、彩色提示框、目录、页脚——全部自动排好，不用在公众号里手动调。

## 二、安装（3 步）

### 第 1 步：准备 Python 环境

需要 Python 3.9+（开发环境为 3.13）。

### 第 2 步：安装依赖

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

> 脚本首次运行也会自动检测并安装缺失依赖，这一步可以跳过。

### 第 3 步：拿到技能目录

把 `wechat-publisher/` 目录（或解压 `.skill` 包）放到任意位置即可，无需额外安装。

## 三、最快上手（一条命令）

```bash
python scripts/convert_to_wechat.py 我的文章.md 输出.html
```

然后：

1. 浏览器打开 `输出.html`
2. `Ctrl+A` 全选 → `Ctrl+C` 复制
3. 打开公众号编辑器（mp.weixin.qq.com）→ 新建图文 → `Ctrl+V` 粘贴
4. 手机预览 → 调整 → 发布

## 四、写文章时的约定

### front-matter 元数据（可选）

文章开头可以写：

```markdown
---
title: 我的文章标题
author: 你的名字
date: 2026-07-17
abstract: 一句话摘要
theme: accent
copyright: © 2026 你的名字
---
```

### Callout 框（四选一）

```markdown
> [!NOTE] 知识框标题
> 内容……

> [!TIP] 提示框标题
> 内容……

> [!WARNING] 注意框标题
> 内容……

> [!PRACTICE] 实践框标题
> 内容……
```

也可以用表情快捷写法：`> 📘` / `> 💡` / `> ⚠️` / `> 🔧`。

## 五、常用命令参考

| 命令 | 作用 |
|------|------|
| `--theme accent` | 切换配色主题（default/accent/minimal/warm/forest） |
| `--theme warm` | 温暖落日橙主题 |
| `--formats all` | 同时输出公众号 HTML + 知乎 Markdown + 纯文本 |
| `--embed-images` | 本地图片内嵌为 base64 |
| `--no-toc` | 关闭自动目录 |
| `--no-footer` | 关闭页脚 |
| `--title/--author/--date/--abstract` | 命令行覆盖元数据 |
| `--new tutorial 新文章.md` | 从模板生成新文章骨架 |
| `--list-themes` | 列出所有主题 |

## 六、从模板起稿

```bash
python scripts/convert_to_wechat.py --new tutorial 我的教程.md --author WangChunYan
```

可用模板：`tutorial`（技术教程）、`learning`（学习心得）、`review`（复盘总结）、`product`（产品介绍）。

## 七、验证是否可用

```bash
python tests/test_converter.py
```

输出 `6/6 通过` 即表示技能工作正常。

## 八、常见问题

| 问题 | 解决 |
|------|------|
| 提示缺依赖 | 运行 `pip install markdown beautifulsoup4 python-docx lxml` |
| 中文文件名乱码 | 已内置 UTF-8/GBK 自动回退，一般不会出现 |
| 图片粘贴后消失 | SVG 会丢失，请用 PNG；本地图片加 `--embed-images` |
| 目录点了没反应 | 公众号不支持页内锚点，目录按纯文字列表生成，属正常现象 |
| 代码块换行 | 代码块已设置自动换行，长命令不会溢出手机屏幕 |

---

*更多细节见技能目录内的 `SKILL.md` 与 `references/wechat_restrictions.md`。*
