# WangChunYan_C4B_拿来说明：从 starter kit 拿了什么、改了什么、为什么

> 原则：**拿来主义 = 理解 → 改造 → 超越**，不是抄，也不是从零重写。

---

## 一、我拿了什么（保留的基座）

从 `c4b-wechat-publisher-starter` 完整读懂了它的结构，并**保留了它最核心、最正确的东西**：

| 保留项 | 具体内容 | 为什么保留 |
|--------|----------|-----------|
| 流水线骨架 | `read → sanitize → style → clean → output` | 这条转换管线是成熟的正确范式，没必要推翻 |
| 函数结构 | `read_markdown / read_docx / sanitize / apply_styles / clean_attributes / convert / main` | 函数职责划分清晰，便于扩展 |
| 依赖选型 | `markdown + beautifulsoup4 + python-docx + lxml` | 成熟、稳定、够用，不重复造轮子 |
| 公众号规则 | `ALLOWED_TAGS / FORBIDDEN_TAGS / ALLOWED_CSS` 三张白黑名单 | 这是对公众号限制的正确建模 |
| Markdown 扩展 | `extra / fenced_code / nl2br / sane_lists` | 覆盖表格、代码、脚注等常用语法 |
| 自动装依赖 | `install_dependencies()` | 降低使用门槛，保留 |
| 参考文档 | `references/wechat_styles.md`、`references/wechat_restrictions.md` | 写得清楚，在其上增补主题与限制 |

## 二、我改了什么（在保留之上做的调整）

| 改动项 | starter 原版 | 我的版本 | 为什么改 |
|--------|-------------|----------|----------|
| 样式配置 | 写死在 `STYLES` 字典里 | 抽成 `THEMES` 字典 + 主题参数 | 改配色不再改代码，一条 `--theme` 切换 |
| 消毒流程 | 独立函数逐个处理 | 增加 callout 识别、`split_br_lines` 换行拆分 | 支持多段落 callout，标题与正文不再粘连 |
| blockquote | 一律转灰色引用框 | 区分 callout 框与普通引用 | callout 是公众号排版核心元素 |
| 输出方式 | 只输出 HTML | 增加 `--formats all` 多格式输出 | 一次写作，多渠道分发 |
| 入口 | 只有 `input output` 两个位置参数 | 完整 `argparse` 参数体系 | 让每条新能力都有开关 |
| 中文字符串打印 | 无处理 | stdout/stderr 强制 UTF-8 + errors=replace | Windows GBK 控制台打印 emoji 不崩溃 |

## 三、我加了什么（新增的九项能力）

按"对别人最有用"排序：

1. **多主题系统**（default / accent / minimal / warm / forest）
2. **Callout 框**（📘知识 / 🔧实践 / ⚠️注意 / 💡提示，支持 `[!NOTE]` 与表情两种写法）
3. **自动目录**（从 h2/h3 生成，长文必备）
4. **文章元数据**（front-matter：标题/作者/日期/摘要/主题/版权）
5. **页脚版权声明**（自动追加，可自定义）
6. **中文排版优化**（中英文自动空格，只加字母边界，不拆 `第1步`）
7. **本地图片内嵌**（PNG/JPG → base64）
8. **多格式输出**（公众号 HTML + 知乎 Markdown + 纯文本）
9. **文章模板**（技术教程 / 学习心得 / 复盘总结 / 产品介绍）

## 四、为什么是这九项（选择的依据）

我选能力的原则，是回到 C4 的**四条件**：

- **可复用**：主题、callout、目录、模板——别人拿到就能直接生成自己的文章
- **可执行**：每条能力都是一个命令行开关，一条命令跑通
- **可验证**：`tests/test_converter.py` 用 6 项断言自动检验产出
- **IO 明确**：输入 md/docx，输出公众号 HTML（+ 知乎/纯文本）

其中 **callout 框 + 自动目录**是"公众号排版核心元素"，**多主题**是"个性化"的体现，
**多格式输出 + 模板**对应 Level 4 的"完整发布流水线"。

## 五、我参考了什么

| 资源 | 我用了什么 |
|------|-----------|
| `c4b-wechat-publisher-starter.zip` | 拿来主义基座（见上） |
| `CHALLENGE.md` 的"缺少的能力"清单 | 直接作为新能力的选题池 |
| `references/wechat_restrictions.md` | 图片 base64 / SVG 会丢失 的规则来源 |
| skill-creator 方法论 | intent → interview → draft → test → iterate 的开发流程 |

---

*结论：保留成熟骨架（约 40%），改造皮肤与交互（约 30%），新增价值能力（约 30%）。*
