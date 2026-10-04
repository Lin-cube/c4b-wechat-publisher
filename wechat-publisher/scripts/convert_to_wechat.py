#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Publisher — Markdown / Word → 微信公众号 HTML
====================================================
WangChunYan 定制版（基于 c4b-wechat-publisher-starter 改造）

在 starter kit 的「read → sanitize → style → clean → output」骨架之上，
新增能力（Level 2 + Level 4）：

  1.  多主题系统   --theme default|accent|minimal|warm|forest
  2.  Callout 框   > [!NOTE] / > [!TIP] / > [!WARNING] / > [!PRACTICE] / 表情快捷写法
  3.  自动目录     --toc / --no-toc
  4.  文章元数据   头部 front-matter（title/author/date/abstract/theme/copyright）
  5.  页脚版权声明 --footer / front-matter 的 copyright
  6.  中文排版优化 中英文自动空格（盘古之白，仅字母边界，不拆"第1步"）
  7.  本地图片内嵌 --embed-images（PNG/JPG → base64）
  8.  多格式输出   --formats wechat,zhihu,plain
  9.  模板系统     --new <template> <out.md>（技术教程/学习心得/复盘总结/产品介绍）

用法：
    python convert_to_wechat.py input.md output.html
    python convert_to_wechat.py input.md output.html --theme accent
    python convert_to_wechat.py input.md output.html --formats all
    python convert_to_wechat.py --new tutorial my_article.md
    python convert_to_wechat.py --list-themes
"""

import sys
import os
import re
import argparse
import base64
import datetime
import mimetypes
from pathlib import Path

# Windows 控制台可能是 GBK，避免打印 emoji 时 UnicodeEncodeError
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, 'reconfigure'):
        try:
            _stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


# ============================================================
# 依赖自动安装（保留自 starter kit）
# ============================================================

def install_dependencies():
    missing = []
    try:
        import markdown  # noqa: F401
    except ImportError:
        missing.append("markdown")
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        missing.append("beautifulsoup4")
    try:
        from docx import Document  # noqa: F401
    except ImportError:
        missing.append("python-docx")
    try:
        import lxml  # noqa: F401
    except ImportError:
        missing.append("lxml")
    if missing:
        print(f"Installing missing packages: {', '.join(missing)} ...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing, "-q"])
        print("Done!\n")


install_dependencies()

import markdown  # noqa: E402
from bs4 import BeautifulSoup, NavigableString  # noqa: E402
from docx import Document  # noqa: E402

# ============================================================
# 常量（保留自 starter kit，并补充）
# ============================================================

ALLOWED_TAGS = {
    'p', 'h2', 'h3', 'ul', 'ol', 'li', 'span', 'img', 'a',
    'table', 'tr', 'th', 'td', 'br',
}

FORBIDDEN_TAGS = {'script', 'style', 'iframe', 'h1', 'div', 'video', 'audio', 'svg'}

ALLOWED_CSS = {
    'color', 'background-color', 'font-size', 'font-weight', 'font-family',
    'line-height', 'text-align', 'font-style', 'margin', 'margin-top',
    'margin-bottom', 'padding', 'border', 'border-left', 'border-top',
    'border-collapse', 'text-decoration', 'max-width', 'width', 'border-radius',
    'display', 'vertical-align', 'letter-spacing', 'word-break',
}

# ============================================================
# 主题系统（新增）——多套配色，一条 --theme 即可切换
# ============================================================

THEMES = {
    "default": {
        "label": "默认 · 中性灰",
        "heading_color": "#333333",
        "body_color": "#333333",
        "link_color": "#576b95",
        "accent": "#576b95",
        "code_bg": "#f6f8fa",
        "code_color": "#24292e",
        "inline_code_bg": "#f2f3f5",
        "inline_code_color": "#d63384",
        "blockquote_bg": "#f7f7f7",
        "blockquote_color": "#666666",
        "blockquote_border": "#d0d0d0",
        "table_header_bg": "#f6f8fa",
        "table_border": "#e0e0e0",
        "meta_color": "#9a9a9a",
        "toc_bg": "#fafafa",
        "toc_border": "#e0e0e0",
    },
    "accent": {
        "label": "强调 · 科技蓝",
        "heading_color": "#1a5fb4",
        "body_color": "#333333",
        "link_color": "#1a73e8",
        "accent": "#1a73e8",
        "code_bg": "#f2f7ff",
        "code_color": "#0b3d91",
        "inline_code_bg": "#e8f0fe",
        "inline_code_color": "#1a5fb4",
        "blockquote_bg": "#f0f7ff",
        "blockquote_color": "#40506a",
        "blockquote_border": "#1a73e8",
        "table_header_bg": "#e8f0fe",
        "table_border": "#d5e3f8",
        "meta_color": "#8a94a6",
        "toc_bg": "#f4f8fd",
        "toc_border": "#cfe0f5",
    },
    "minimal": {
        "label": "极简 · 黑白灰",
        "heading_color": "#111111",
        "body_color": "#333333",
        "link_color": "#555555",
        "accent": "#111111",
        "code_bg": "#fafafa",
        "code_color": "#111111",
        "inline_code_bg": "#f3f3f3",
        "inline_code_color": "#111111",
        "blockquote_bg": "#fafafa",
        "blockquote_color": "#555555",
        "blockquote_border": "#999999",
        "table_header_bg": "#f5f5f5",
        "table_border": "#e0e0e0",
        "meta_color": "#999999",
        "toc_bg": "#fafafa",
        "toc_border": "#e0e0e0",
    },
    "warm": {
        "label": "温暖 · 落日橙",
        "heading_color": "#c2410c",
        "body_color": "#3f3a36",
        "link_color": "#e65100",
        "accent": "#e65100",
        "code_bg": "#fff7ed",
        "code_color": "#7c2d12",
        "inline_code_bg": "#ffedd5",
        "inline_code_color": "#c2410c",
        "blockquote_bg": "#fff8e8",
        "blockquote_color": "#6b5b45",
        "blockquote_border": "#ff9800",
        "table_header_bg": "#fff1dc",
        "table_border": "#f0dcc0",
        "meta_color": "#a09280",
        "toc_bg": "#fdf6ec",
        "toc_border": "#f0dfc0",
    },
    "forest": {
        "label": "自然 · 墨绿",
        "heading_color": "#14532d",
        "body_color": "#333333",
        "link_color": "#16a34a",
        "accent": "#15803d",
        "code_bg": "#f0fdf4",
        "code_color": "#14532d",
        "inline_code_bg": "#dcfce7",
        "inline_code_color": "#15803d",
        "blockquote_bg": "#f0fdf4",
        "blockquote_color": "#3f5a49",
        "blockquote_border": "#22c55e",
        "table_header_bg": "#ecfdf1",
        "table_border": "#d3e8d8",
        "meta_color": "#8aa392",
        "toc_bg": "#f4faf5",
        "toc_border": "#d3e8d8",
    },
}

DEFAULT_THEME = "default"

# ============================================================
# Callout 类型（新增）——📘知识 / 🔧实践 / ⚠️注意 / 💡提示
# ============================================================

CALLOUT_STYLES = {
    "note": (
        "background-color: #eef4ff; border-left: 4px solid #4a7dff; color: #1f3a5f; "
        "padding: 14px 16px; margin: 14px 0; border-radius: 4px; "
        "font-size: 15px; line-height: 1.75;"
    ),
    "practice": (
        "background-color: #e9fbf0; border-left: 4px solid #22a06b; color: #14532d; "
        "padding: 14px 16px; margin: 14px 0; border-radius: 4px; "
        "font-size: 15px; line-height: 1.75;"
    ),
    "warning": (
        "background-color: #fff4e5; border-left: 4px solid #f59e0b; color: #7c2d12; "
        "padding: 14px 16px; margin: 14px 0; border-radius: 4px; "
        "font-size: 15px; line-height: 1.75;"
    ),
    "tip": (
        "background-color: #f6efff; border-left: 4px solid #8b5cf6; color: #4c1d95; "
        "padding: 14px 16px; margin: 14px 0; border-radius: 4px; "
        "font-size: 15px; line-height: 1.75;"
    ),
}

CALLOUT_LABELS = {
    "note": "📘 知识",
    "practice": "🔧 实践",
    "warning": "⚠️ 注意",
    "tip": "💡 提示",
}

CALLOUT_EMOJI = {
    "📘": "note",
    "🔧": "practice",
    "⚠️": "warning",
    "💡": "tip",
    "📌": "tip",
    "✅": "practice",
}


def detect_callout(head_text):
    """从 blockquote 首行识别 callout 类型与标题，返回 (type, title) 或 None。"""
    head = head_text.strip()
    m = re.match(r'^\[!\s*(note|tip|warning|practice)\s*\]\s*(.*)$', head, re.IGNORECASE)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    for emoji, typ in CALLOUT_EMOJI.items():
        if head.startswith(emoji):
            return typ, head[len(emoji):].strip()
    return None


def split_br_lines(p_tag):
    """把 <p> 内容按 <br> 拆成多行文本（保留嵌套标签内文字）。"""
    lines = []
    buf = []

    def flush():
        text = ''.join(buf).strip()
        if text:
            lines.append(text)
        del buf[:]

    def walk(el):
        for child in el.children:
            if isinstance(child, NavigableString):
                buf.append(str(child))
            elif getattr(child, 'name', None) == 'br':
                flush()
            elif getattr(child, 'name', None) is not None:
                walk(child)

    walk(p_tag)
    flush()
    return lines or [p_tag.get_text(' ', strip=True)]


# ============================================================
# 输入读取（保留并强化自 starter kit）
# ============================================================

def _read_text(filepath):
    """UTF-8 优先，失败回退 GBK。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='gbk') as f:
            return f.read()


def parse_front_matter(md_text):
    """解析头部 front-matter，返回 (meta_dict, body_text)。"""
    meta = {}
    body = md_text
    m = re.match(r'^\ufeff?---\s*\n(.*?)\n---\s*\n?', md_text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line or ':' not in line:
                continue
            key, _, value = line.partition(':')
            key = key.strip().lower()
            value = value.strip().strip('"').strip("'")
            meta[key] = value
        body = md_text[m.end():]
    return meta, body


def read_markdown(filepath):
    """把 Markdown 转成 HTML 字符串（保留 starter 的扩展配置）。"""
    content = _read_text(filepath)
    html = markdown.markdown(content, extensions=[
        'extra', 'fenced_code', 'nl2br', 'sane_lists', 'tables',
    ])
    return html


def read_docx(filepath):
    """从 Word .docx 提取内容为 HTML 字符串。"""
    doc = Document(filepath)
    parts = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style_name = para.style.name if para.style else ''
        if style_name.startswith('Heading'):
            level = style_name.replace('Heading ', '')
            tag = 'h2' if level in ('1', '2') else 'h3'
            parts.append(f'<{tag}>{text}</{tag}>')
        else:
            p_html = '<p>'
            for run in para.runs:
                t = run.text
                if not t:
                    continue
                if run.bold and run.italic:
                    p_html += f'<span style="font-weight:bold;font-style:italic;">{t}</span>'
                elif run.bold:
                    p_html += f'<span style="font-weight:bold;">{t}</span>'
                elif run.italic:
                    p_html += f'<span style="font-style:italic;">{t}</span>'
                else:
                    p_html += t
            p_html += '</p>'
            parts.append(p_html)
    return '\n'.join(parts)


# ============================================================
# HTML 消毒与结构化转换
# ============================================================

def sanitize(soup):
    """对 HTML 做公众号兼容处理（在 starter 基础上加入 callout 转换）。"""
    # 1) 移除禁止标签（script/style/iframe/...）
    for tag_name in FORBIDDEN_TAGS:
        for el in soup.find_all(tag_name):
            el.decompose()

    # 2) h1 → h2
    for h1 in soup.find_all('h1'):
        h1.name = 'h2'

    # 3) div → p
    for div in soup.find_all('div'):
        div.name = 'p'

    # 4) <pre><code> → 带样式的 <p>（代码块，标记 monospace 供排版跳过）
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        code_text = code.get_text() if code else pre.get_text()
        p = soup.new_tag('p')
        p.string = code_text
        p['style'] = "font-family: Consolas, Monaco, 'Courier New', monospace;"
        p['data-role'] = 'code-block'
        pre.replace_with(p)

    # 5) 行内 <code> → 带样式 <span>
    for code in soup.find_all('code'):
        span = soup.new_tag('span')
        span.string = code.get_text()
        span['style'] = "font-family: Consolas, Monaco, 'Courier New', monospace;"
        span['data-role'] = 'code-inline'
        code.replace_with(span)

    # 6) <blockquote> → callout 框 或 普通引用 <p>
    for bq in soup.find_all('blockquote'):
        ps = bq.find_all('p')
        all_lines = []
        if ps:
            for pp in ps:
                all_lines.extend(split_br_lines(pp))
        else:
            all_lines = [bq.get_text(' ', strip=True)]

        head_line = all_lines[0] if all_lines else ''
        detected = detect_callout(head_line)

        if detected:
            typ, title = detected
            body_lines = all_lines[1:]
            p = soup.new_tag('p')
            p['style'] = CALLOUT_STYLES[typ]
            label = CALLOUT_LABELS[typ]
            head_span = soup.new_tag('span')
            head_span['style'] = 'font-weight: bold;'
            head_span.string = f"{label} ｜ {title}" if title else label
            p.append(head_span)
            for line in body_lines:
                line = line.strip()
                if not line:
                    continue
                p.append(soup.new_tag('br'))
                p.append(NavigableString(line))
            bq.replace_with(p)
        else:
            p = soup.new_tag('p')
            p['data-role'] = 'blockquote'
            p.append(NavigableString('　'.join(all_lines)))
            bq.replace_with(p)

    # 7) <strong>/<b> → 加粗 <span>
    for tag in soup.find_all(['strong', 'b']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-weight: bold;'
        tag.replace_with(span)

    # 8) <em>/<i> → 斜体 <span>
    for tag in soup.find_all(['em', 'i']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-style: italic;'
        tag.replace_with(span)

    return soup


# ============================================================
# 头部 / 目录 / 页脚（新增）
# ============================================================

def build_header(soup, meta, theme):
    """构建文章头部：标题 + 作者/日期 + 摘要。返回元素列表。"""
    els = []
    title = meta.get('title') or '未命名文章'

    title_el = soup.new_tag('h2')
    title_el['data-role'] = 'title'
    title_el['style'] = (
        f"font-size: 24px; font-weight: bold; line-height: 1.5; "
        f"color: {theme['heading_color']}; text-align: center; "
        f"margin: 8px 0 16px 0;"
    )
    title_el.string = title
    els.append(title_el)

    meta_parts = []
    if meta.get('author'):
        meta_parts.append(f"作者：{meta['author']}")
    if meta.get('date'):
        meta_parts.append(f"{meta['date']}")
    if meta_parts:
        meta_el = soup.new_tag('p')
        meta_el['data-role'] = 'meta'
        meta_el['style'] = (
            f"font-size: 14px; color: {theme['meta_color']}; text-align: center; "
            f"margin: 0 0 14px 0; letter-spacing: 1px;"
        )
        meta_el.string = '　'.join(meta_parts)
        els.append(meta_el)

    abstract = meta.get('abstract') or meta.get('summary')
    if abstract:
        ab_el = soup.new_tag('p')
        ab_el['data-role'] = 'abstract'
        ab_el['style'] = (
            f"background-color: {theme['toc_bg']}; border-left: 4px solid {theme['accent']}; "
            f"color: {theme['body_color']}; padding: 12px 16px; margin: 12px 0; "
            f"font-size: 15px; line-height: 1.75; border-radius: 4px;"
        )
        ab_el.string = abstract
        els.append(ab_el)

    return els


def build_toc(soup, theme):
    """从 h2/h3 生成目录，返回一个 <p> 或 None。"""
    headings = [
        el for el in soup.body.find_all(['h2', 'h3'])
        if el.get('data-role') != 'title' and el.get_text(strip=True)
    ]
    if not headings:
        return None

    box = soup.new_tag('p')
    box['data-role'] = 'toc'
    box['style'] = (
        f"background-color: {theme['toc_bg']}; border: 1px solid {theme['toc_border']}; "
        f"border-radius: 6px; padding: 14px 16px; margin: 14px 0; "
        f"font-size: 15px; line-height: 1.9; color: {theme['body_color']};"
    )
    title = soup.new_tag('span')
    title['style'] = f"font-weight: bold; color: {theme['heading_color']};"
    title.string = '📑 目录'
    box.append(title)

    def _add(text, indent, bold=False):
        if box.contents:
            box.append(soup.new_tag('br'))
        s = soup.new_tag('span')
        s['style'] = (
            f"font-weight: {'bold' if bold else 'normal'}; "
            f"color: {theme['heading_color'] if bold else theme['body_color']};"
            f"display: inline-block; padding-left: {indent}px;"
        )
        s.string = text
        box.append(s)

    for el in headings:
        txt = el.get_text(strip=True)
        if el.name == 'h2':
            _add(txt, 0, bold=True)
        else:
            _add('· ' + txt, 18, bold=False)
    return box


def build_footer(soup, meta, theme):
    """构建页脚版权声明，返回 <p>。"""
    footer = soup.new_tag('p')
    footer['data-role'] = 'footer'
    copyright_text = meta.get('copyright') or meta.get('footer')
    author = meta.get('author') or ''
    year = (meta.get('date') or '')[:4] or str(datetime.date.today().year)

    footer['style'] = (
        f"border-top: 1px solid {theme['table_border']}; "
        f"color: {theme['meta_color']}; font-size: 13px; text-align: center; "
        f"padding-top: 14px; margin-top: 30px; line-height: 1.9;"
    )
    lines = []
    if copyright_text:
        lines.append(copyright_text)
    else:
        lines.append(f"© {year} {author}".strip() if author else f"© {year}")
    lines.append("本文由 wechat-publisher（WangChunYan 定制版）生成")
    footer.append(NavigableString('　·　'.join(lines)))
    return footer


# ============================================================
# 样式应用 / 属性清理 / 中文排版 / 图片内嵌
# ============================================================

def apply_styles(soup, theme):
    """按主题给元素加 inline CSS（已有 style 的元素不覆盖）。"""
    h2 = (
        f"font-size: 21px; font-weight: bold; line-height: 1.6; "
        f"color: {theme['heading_color']}; margin: 26px 0 12px 0;"
    )
    h3 = (
        f"font-size: 17px; font-weight: bold; line-height: 1.6; "
        f"color: {theme['heading_color']}; margin: 20px 0 8px 0;"
    )
    p = (
        f"font-size: 16px; line-height: 1.8; color: {theme['body_color']}; "
        f"margin: 12px 0; text-align: justify; word-break: break-word;"
    )
    li = f"font-size: 16px; line-height: 1.8; color: {theme['body_color']}; margin: 6px 0;"
    blockquote = (
        f"background-color: {theme['blockquote_bg']}; color: {theme['blockquote_color']}; "
        f"padding: 12px 16px; margin: 14px 0; border-left: 4px solid {theme['blockquote_border']};"
        f"font-size: 15px; line-height: 1.75; border-radius: 4px;"
    )
    code_inline = (
        f"background-color: {theme['inline_code_bg']}; color: {theme['inline_code_color']}; "
        f"font-size: 14px; padding: 2px 6px; border-radius: 3px;"
    )
    code_block = (
        f"background-color: {theme['code_bg']}; color: {theme['code_color']}; font-size: 13px; "
        f"line-height: 1.6; padding: 14px 16px; margin: 14px 0; border-radius: 6px;"
        f"white-space: pre-wrap; word-break: break-all;"
    )
    table = f"border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;"
    th = (
        f"background-color: {theme['table_header_bg']}; color: {theme['heading_color']}; "
        f"font-weight: bold; padding: 8px 10px; text-align: left; "
        f"border: 1px solid {theme['table_border']};"
    )
    td = f"padding: 8px 10px; border: 1px solid {theme['table_border']}; color: {theme['body_color']};"
    a = f"color: {theme['link_color']}; text-decoration: underline;"

    style_map = {'h2': h2, 'h3': h3, 'p': p, 'li': li, 'table': table,
                 'th': th, 'td': td, 'a': a}
    for tag_name, style in style_map.items():
        for el in soup.find_all(tag_name):
            if el.get('style'):
                continue  # 保留手工设定（callout/代码/头部/目录等）
            el['style'] = style

    # 代码块/行内代码补全样式（避免与上面的通用 p 冲突）
    for el in soup.find_all(attrs={'data-role': 'code-block'}):
        base = el.get('style', '')
        el['style'] = base + code_block
    for el in soup.find_all(attrs={'data-role': 'code-inline'}):
        base = el.get('style', '')
        el['style'] = base + code_inline
    for el in soup.find_all(attrs={'data-role': 'blockquote'}):
        el['style'] = blockquote

    return soup


def clean_attributes(soup):
    """移除 class/id/data-*/on*，并把不在白名单的标签 unwrap。"""
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            if attr in ('class', 'id') or attr.startswith('data-') or attr.startswith('on'):
                del tag.attrs[attr]
        if tag.name not in ALLOWED_TAGS and tag.name not in ('html', 'head', 'body', '[document]'):
            tag.unwrap()
    return soup


_CJK = r'\u4e00-\u9fff\u3400-\u4dbf'

# 中文字符 后接 拉丁字母 → 加空格
_RE_CJK_LATIN = re.compile(f'([{_CJK}])([A-Za-z])')
# 拉丁字母 后接 中文字符 → 加空格
_RE_LATIN_CJK = re.compile(f'([A-Za-z])([{_CJK}])')


def pangu_spacing(soup):
    """中英文自动空格（仅字母边界，不拆 '第1步' / '10倍' 这类数字边界）。"""
    def _is_code(el):
        node = el
        while node is not None:
            if getattr(node, 'name', None) and node.get('style'):
                if 'monospace' in node['style']:
                    return True
            node = getattr(node, 'parent', None)
        return False

    for txt in list(soup.find_all(string=True)):
        parent = txt.parent
        if parent is None or _is_code(parent):
            continue
        if not isinstance(txt, NavigableString):
            continue
        s = txt.string
        if not s or not re.search(f'[{_CJK}]', s):
            continue
        s2 = _RE_CJK_LATIN.sub(r'\1 \2', s)
        s2 = _RE_LATIN_CJK.sub(r'\1 \2', s2)
        if s2 != s:
            txt.replace_with(NavigableString(s2))
    return soup


def embed_images(soup, base_dir):
    """把本地图片 src 内嵌为 base64 data URI（PNG/JPG/GIF）。"""
    count = 0
    for img in soup.find_all('img'):
        src = (img.get('src') or '').strip()
        if not src or src.startswith(('http://', 'https://', 'data:')):
            continue
        local = Path(src)
        if not local.is_absolute():
            local = Path(base_dir) / local
        if not local.exists():
            print(f"⚠️  图片不存在，跳过：{src}")
            continue
        data = local.read_bytes()
        mime = mimetypes.guess_type(str(local))[0] or 'image/png'
        if mime.split('/')[-1] == 'svg':
            print(f"⚠️  SVG 在公众号会丢失，跳过：{src}")
            continue
        img['src'] = f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        count += 1
    if count:
        print(f"🖼️  已内嵌 {count} 张本地图片为 base64")
    return soup


# ============================================================
# 主转换流水线
# ============================================================

def resolve_title(meta, body_md):
    """确定文章标题：优先 front-matter，其次正文首个 '#' 标题。"""
    title = meta.get('title')
    if title:
        return title, body_md
    m = re.search(r'^#{1}\s+(.+?)\s*$', body_md, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        body_md = body_md[:m.start()] + body_md[m.end():]
        body_md = body_md.lstrip('\n')
    return title, body_md


def convert(input_path, output_path, args):
    """read → sanitize → header → toc → style → clean → pangu → images → footer → output。"""
    path = Path(input_path)
    if not path.exists():
        print(f"❌ 错误：找不到文件 '{input_path}'")
        return False

    theme = THEMES.get(args.theme, THEMES[DEFAULT_THEME])
    ext = path.suffix.lower()
    meta = {}
    source_md = None

    print(f"📖 读取 {path.name} ({ext}) ...")
    if ext == '.md':
        raw = _read_text(input_path)
        meta, body_md = parse_front_matter(raw)
        meta.setdefault('theme', args.theme)
        if meta.get('theme') and meta['theme'] in THEMES:
            theme = THEMES[meta['theme']]
        title, body_md = resolve_title(meta, body_md)
        if not meta.get('title'):
            meta['title'] = title
        source_md = body_md
        html = read_markdown_of(body_md)
    elif ext == '.docx':
        html = read_docx(input_path)
        title = meta.get('title') or path.stem
        meta['title'] = title
    elif ext in ('.html', '.htm'):
        html = _read_text(input_path)
        title = meta.get('title') or path.stem
        meta['title'] = title
    else:
        print(f"❌ 不支持的格式：{ext}（支持 .md / .docx / .html）")
        return False

    # CLI 覆盖 front-matter（--footer 是布尔开关，不进入 meta）
    for key in ('title', 'author', 'date', 'abstract', 'copyright'):
        val = getattr(args, key, None)
        if val:
            meta[key] = val

    print("🧹 消毒 HTML（移除禁用标签 / 转换 h1·div / 识别 callout）...")
    soup = BeautifulSoup(html, 'lxml')
    soup = sanitize(soup)

    body = soup.body or soup

    print("🎨 应用主题样式（%s）..." % theme['label'])
    header_els = build_header(soup, meta, theme)
    for i, el in enumerate(header_els):
        body.insert(i, el)

    insert_at = len(header_els)
    if args.toc:
        toc_el = build_toc(soup, theme)
        if toc_el is not None:
            body.insert(insert_at, toc_el)
            print("📑 已生成目录")

    soup = apply_styles(soup, theme)
    soup = clean_attributes(soup)

    if args.pangu:
        soup = pangu_spacing(soup)
        print("🈶 已应用中英文自动空格")

    if args.embed_images:
        soup = embed_images(soup, path.parent)

    if args.footer:
        footer_el = build_footer(soup, meta, theme)
        body.append(footer_el)

    # 提取 body 内容
    content = '\n'.join(str(child) for child in body.children if str(child).strip())

    output_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta.get('title', 'WeChat Article')}</title>
</head>
<body style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;">
{content}
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ 完成！{output_path}（{size_kb:.1f} KB）")

    # 多格式输出
    write_extra_formats(args, output_path, meta, source_md, soup)

    print("\n📋 下一步：")
    print("   1. 浏览器打开输出 HTML 预览")
    print("   2. Ctrl+A → Ctrl+C 全选复制")
    print("   3. 打开 mp.weixin.qq.com → 新建图文 → Ctrl+V 粘贴")
    print("   4. 图片按需上传素材库，手机预览 → 发布")
    return True


def read_markdown_of(md_text):
    """把 markdown 文本转 HTML（供 convert 内部复用扩展配置）。"""
    return markdown.markdown(md_text, extensions=[
        'extra', 'fenced_code', 'nl2br', 'sane_lists', 'tables',
    ])


def write_extra_formats(args, output_path, meta, source_md, soup):
    """Level 4：同一内容输出公众号 HTML + 知乎 Markdown + 纯文本。"""
    formats = {f.strip().lower() for f in args.formats.split(',') if f.strip()}
    if 'all' in formats:
        formats = {'wechat', 'zhihu', 'plain'}
    formats.discard('wechat')  # wechat 已输出
    if not formats:
        return

    out = Path(output_path)
    stem = out.with_suffix('')

    if 'zhihu' in formats and source_md is not None:
        zhihu_path = f"{stem}_zhihu.md"
        title = meta.get('title', '未命名文章')
        meta_lines = []
        if meta.get('author'):
            meta_lines.append(f"> 作者：{meta['author']}")
        if meta.get('date'):
            meta_lines.append(f"> 日期：{meta['date']}")
        header = f"# {title}\n\n" + ('\n'.join(meta_lines) + '\n\n' if meta_lines else '')
        with open(zhihu_path, 'w', encoding='utf-8') as f:
            f.write(header + source_md.strip() + '\n')
        print(f"📝 已输出知乎 Markdown：{zhihu_path}")

    if 'plain' in formats:
        plain_path = f"{stem}_plain.txt"
        text = soup.get_text('\n', strip=True)
        with open(plain_path, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
        print(f"📄 已输出纯文本：{plain_path}")


# ============================================================
# 模板系统（Level 4）
# ============================================================

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates'

TEMPLATE_META = {
    "tutorial": {"title": "技术教程模板标题", "abstract": "一句话说清这篇教程解决什么问题、读者能学会什么。"},
    "learning": {"title": "学习心得模板标题", "abstract": "一句话概括这段学习经历与最重要的一个收获。"},
    "review": {"title": "复盘总结模板标题", "abstract": "一句话概括这次复盘的对象与核心结论。"},
    "product": {"title": "产品介绍模板标题", "abstract": "一句话说明这个产品是什么、解决谁的什么问题。"},
}


def generate_from_template(template, output_path, author):
    tpl_file = TEMPLATES_DIR / f"{template}.md"
    if not tpl_file.exists():
        print(f"❌ 模板不存在：{template}")
        print(f"   可用模板：{', '.join(sorted(TEMPLATE_META.keys()))}")
        print(f"   目录：{TEMPLATES_DIR}")
        return False
    content = _read_text(str(tpl_file))
    today = datetime.date.today().isoformat()
    content = content.replace("{{DATE}}", today)
    content = content.replace("{{AUTHOR}}", author or "你的名字")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已从模板 '{template}' 生成：{output_path}")
    print("   接下来编辑内容，然后运行：")
    print(f"   python scripts/convert_to_wechat.py {output_path} 输出.html --theme accent")
    return True


# ============================================================
# 入口
# ============================================================

def build_parser():
    p = argparse.ArgumentParser(
        description="WeChat Publisher — Markdown/Word → 公众号 HTML（WangChunYan 定制版）")
    p.add_argument('input', nargs='?', help='输入文件（.md / .docx / .html）')
    p.add_argument('output', nargs='?', help='输出 HTML 文件')
    p.add_argument('--theme', default=DEFAULT_THEME, choices=list(THEMES.keys()),
                   help='配色主题（默认 default）')
    p.add_argument('--toc', dest='toc', action='store_true', default=True, help='生成目录（默认开）')
    p.add_argument('--no-toc', dest='toc', action='store_false', help='不生成目录')
    p.add_argument('--title', help='覆盖文章标题')
    p.add_argument('--author', help='覆盖作者名')
    p.add_argument('--date', help='覆盖日期（YYYY-MM-DD）')
    p.add_argument('--abstract', help='覆盖摘要')
    p.add_argument('--copyright', help='覆盖版权/页脚文字')
    p.add_argument('--footer', dest='footer', action='store_true', default=True,
                   help='追加页脚版权声明（默认开）')
    p.add_argument('--no-footer', dest='footer', action='store_false', help='不追加页脚')
    p.add_argument('--pangu', dest='pangu', action='store_true', default=True,
                   help='中英文自动空格（默认开）')
    p.add_argument('--no-pangu', dest='pangu', action='store_false', help='关闭中英文空格')
    p.add_argument('--embed-images', action='store_true', default=False,
                   help='本地图片内嵌为 base64')
    p.add_argument('--formats', default='wechat',
                   help='输出格式：wechat,zhihu,plain 或 all（逗号分隔）')
    p.add_argument('--new', metavar='TEMPLATE', help='从模板生成新文章（tutorial/learning/review/product）')
    p.add_argument('--list-themes', action='store_true', help='列出所有主题')
    return p


def main():
    args = build_parser().parse_args()

    if args.list_themes:
        print("可用主题：")
        for key, t in THEMES.items():
            print(f"  {key:<9} {t['label']}")
        return

    if args.new:
        if not args.input:
            print("用法：python convert_to_wechat.py --new <模板> <输出.md> [--author 名字]")
            sys.exit(1)
        ok = generate_from_template(args.new, args.input, args.author)
        sys.exit(0 if ok else 1)

    if not args.input or not args.output:
        build_parser().print_help()
        sys.exit(1)

    ok = convert(args.input, args.output, args)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
