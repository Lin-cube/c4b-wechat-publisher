# WeChat Official Account HTML 限制参考

公众号编辑器对 HTML 非常严格。本技能会自动强制执行以下规则。

## 允许的标签

```
p, h2, h3, ul, ol, li, span, img, a, table, tr, th, td, br
```

## 禁止的标签

| 标签 | 原因 | 处理 |
|------|------|------|
| `<h1>` | 公众号把 h1 留给文章标题 | 转为 `<h2>` |
| `<div>` | 渲染不可靠 | 转为 `<p>` |
| `<script>` | 安全，一律剥离 | 移除 |
| `<style>` | CSS 必须内联 | 移到 `style=""` |
| `<iframe>` | 外部嵌入被禁 | 移除或转链接 |
| `<video>` | 必须用公众号视频组件 | 移除或转链接 |
| `<audio>` | 必须用公众号音频组件 | 移除或转链接 |
| `<svg>` | 保存时消失 | 移除（图片请用 PNG） |

## 禁止的属性

| 属性 | 原因 | 处理 |
|------|------|------|
| `class` | 公众号无 CSS 类 | 移除 |
| `id` | 公众号无元素 ID | 移除 |
| `onclick` 等 | 无 JS 事件 | 移除 |

## CSS 规则

### 必须内联
每个元素都要有自己的 `style="..."`：

```html
<!-- ✅ 正确 -->
<p style="font-size: 16px; color: #333;">你好</p>

<!-- ❌ 错误，公众号会剥离 -->
<style>p { font-size: 16px; color: #333; }</style>
<p>你好</p>
```

### 允许的 CSS 属性
```
color, background-color, font-size, font-weight, font-style, font-family,
line-height, text-align, margin, margin-top, margin-bottom, padding,
border, border-left, border-top, border-collapse, text-decoration,
max-width, width, border-radius, display, vertical-align,
letter-spacing, word-break
```

### 禁止的 CSS
- `position`、`float`、`flex`、`grid` —— 布局属性
- `animation`、`transition` —— 动效属性
- `@media` 查询、`@font-face` 自定义字体

## 图片规则

| 方式 | 是否可行 | 说明 |
|------|----------|------|
| `<img src="https://...">` | ⚠️ | 可访问则可行；公众号可能转存 |
| `<img src="data:image/png;base64,...">` | ✅ | 粘贴时公众号转存到 CDN |
| `<img src="data:image/svg+xml;base64,...">` | ❌ | 保存时消失 |
| 内联 `<svg>...</svg>` | ❌ | 完全剥离 |

**最佳实践**：自包含图片用 PNG base64（`--embed-images`）；照片上传素材库用 CDN URL。

## 文章限制

| 限制 | 数值 |
|------|------|
| 最大文章长度 | 约 2 万汉字 |
| 单篇图片上限 | 100 张 |
| 单张图片大小 | 10 MB |
| 支持的图片格式 | PNG / JPG / GIF |
| GIF 大小上限 | 2 MB |

## 常见坑

1. **保存后格式丢失**：通常用了禁止的标签或 CSS
2. **图片消失**：SVG data URI 或失效外链
3. **间距异常**：公众号折叠 margin 的方式与浏览器不同
4. **代码块损坏**：必须用带 inline 样式的 `<p>`，不能是 `<pre><code>`
5. **表格过宽**：无横向滚动，建议拆分宽表
