# WeChat Publisher — 样式参考（WangChunYan 定制版）

本技能所有样式均以内联 `style="..."` 输出，公众号只认 inline CSS。
主题定义在 `scripts/convert_to_wechat.py` 的 `THEMES` 字典中，以下为各主题的取值参考。

## 主题速览

| 主题 | 标题色 | 强调色 | 适用场景 |
|------|--------|--------|----------|
| `default` 中性灰 | `#333333` | `#576b95` | 通用、正式 |
| `accent` 科技蓝 | `#1a5fb4` | `#1a73e8` | 技术教程、产品介绍 |
| `minimal` 黑白灰 | `#111111` | `#111111` | 极简、文学 |
| `warm` 落日橙 | `#c2410c` | `#e65100` | 学习心得、故事 |
| `forest` 墨绿 | `#14532d` | `#15803d` | 自然、成长 |

## 排版 Typography

### H2（章节标题，公众号最高层级）
```
font-size: 21px; font-weight: bold; line-height: 1.6;
color: {heading_color}; margin: 26px 0 12px 0;
```

### H3（小节标题）
```
font-size: 17px; font-weight: bold; line-height: 1.6;
color: {heading_color}; margin: 20px 0 8px 0;
```

### 正文段落
```
font-size: 16px; line-height: 1.8; color: {body_color};
margin: 12px 0; text-align: justify; word-break: break-word;
```

### 列表项
```
font-size: 16px; line-height: 1.8; color: {body_color}; margin: 6px 0;
```

## 代码 Code

### 行内代码
```
background-color: {inline_code_bg}; color: {inline_code_color};
font-size: 14px; padding: 2px 6px; border-radius: 3px;
```

### 代码块
```
background-color: {code_bg}; color: {code_color}; font-size: 13px;
line-height: 1.6; padding: 14px 16px; border-radius: 6px;
white-space: pre-wrap; word-break: break-all;
```

## 结构 Structural

### 引用块（blockquote）
```
background-color: {blockquote_bg}; color: {blockquote_color};
padding: 12px 16px; border-left: 4px solid {blockquote_border};
border-radius: 4px;
```

### Callout 框（固定配色，跨主题一致）
| 类型 | 背景 | 左框线 | 文字色 |
|------|------|--------|--------|
| 📘 知识 note | `#eef4ff` | `#4a7dff` | `#1f3a5f` |
| 🔧 实践 practice | `#e9fbf0` | `#22a06b` | `#14532d` |
| ⚠️ 注意 warning | `#fff4e5` | `#f59e0b` | `#7c2d12` |
| 💡 提示 tip | `#f6efff` | `#8b5cf6` | `#4c1d95` |

### 表格
```
table: border-collapse: collapse; font-size: 14px; width: 100%;
th:    background-color: {table_header_bg}; border: 1px solid {table_border};
td:    padding: 8px 10px; border: 1px solid {table_border};
```

### 链接
```
color: {link_color}; text-decoration: underline;
```

## 移动端注意事项

- 正文字号最小 16px，手机上更小就难以阅读
- 大多数手机正文显示宽度约 375px，`max-width: 600px` 预览外壳仅用于桌面
- 中文正文最佳行高 1.8（比英文更舒展）
- 正文色避免纯黑 `#000`，`#333` 更柔和
- 图片务必 `max-width: 100%` 防溢出（本地图片内嵌时已处理）

## 自定义新主题

在 `convert_to_wechat.py` 的 `THEMES` 中加一个键即可，字段参考：

```python
"mydark": {
    "label": "深色示例",
    "heading_color": "#...", "body_color": "#...", "link_color": "#...",
    "accent": "#...", "code_bg": "#...", "code_color": "#...",
    "inline_code_bg": "#...", "inline_code_color": "#...",
    "blockquote_bg": "#...", "blockquote_color": "#...", "blockquote_border": "#...",
    "table_header_bg": "#...", "table_border": "#...",
    "meta_color": "#...", "toc_bg": "#...", "toc_border": "#...",
}
```
