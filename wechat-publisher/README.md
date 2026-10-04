# wechat-publisher（WangChunYan 定制版）

把 Markdown / Word 文档转换成**可直接粘贴进公众号编辑器**的 HTML。
基于 `c4b-wechat-publisher-starter` 改造，新增主题、callout 框、自动目录、元数据、页脚、
中文排版、图片内嵌、多格式输出与文章模板。

## 安装

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

（脚本首次运行也会自动检测并安装缺失依赖。）

## 快速上手

```bash
# 基础转换
python scripts/convert_to_wechat.py 我的文章.md 输出.html

# 指定主题 + 多格式输出
python scripts/convert_to_wechat.py 我的文章.md 输出.html --theme accent --formats all

# 从模板新建文章
python scripts/convert_to_wechat.py --new tutorial 新文章.md --author 你的名字
```

然后：浏览器打开 `输出.html` → 全选复制 → 公众号编辑器粘贴。

## 目录结构

```
wechat-publisher/
├── SKILL.md                      主指令（给 AI 看的技能说明）
├── README.md                     本文件
├── scripts/
│   └── convert_to_wechat.py      转换脚本（md/docx → 公众号 HTML）
├── references/
│   ├── wechat_styles.md          样式与主题参考
│   └── wechat_restrictions.md    公众号 HTML 限制规则
├── templates/                    文章模板（tutorial/learning/review/product）
│   ├── tutorial.md
│   ├── learning.md
│   ├── review.md
│   └── product.md
├── examples/
│   ├── sample_article.md         示例输入
│   └── sample_output.html        示例输出
└── tests/
    └── test_converter.py         回归测试（eval）
```

## 能力清单

| 能力 | 说明 |
|------|------|
| 多主题 | 5 套主题，`--theme default/accent/minimal/warm/forest` |
| Callout 框 | `> [!NOTE]` 知识 / `> [!TIP]` 提示 / `> [!WARNING]` 注意 / `> [!PRACTICE]` 实践 |
| 自动目录 | 从 h2/h3 自动生成 |
| 文章元数据 | front-matter：title/author/date/abstract/theme/copyright |
| 页脚版权 | 自动追加 |
| 中文排版 | 中英文自动空格（字母边界） |
| 图片内嵌 | `--embed-images` 本地图片 → base64 |
| 多格式输出 | 公众号 HTML / 知乎 Markdown / 纯文本 |
| 文章模板 | `--new` 一键起稿 |

## 测试

```bash
python tests/test_converter.py
```

6 项断言：无禁用标签、callout 存在、目录存在、页脚存在、中英文空格生效、多格式输出。

## 完整参数

```
python scripts/convert_to_wechat.py --help
```
