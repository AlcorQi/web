# Python网络爬虫项目使用说明

## 项目结构
```
crawler_project/
├── crawler.py          # 主爬虫脚本
├── config.py           # 配置文件
├── requirements.txt    # 项目依赖
├── data/               # 爬取数据存储目录
├── logs/               # 日志文件存储目录
└── utils/              # 工具模块
    ├── logger.py       # 日志工具
    └── data_storage.py # 数据存储工具
```

## 安装依赖

在项目目录下运行以下命令安装所需依赖：

```bash
pip install -r requirements.txt
```

如果需要使用Selenium功能，还需要安装对应的浏览器驱动（如ChromeDriver）。

## 配置说明

项目配置位于 `config.py` 文件中，主要包含：

- `BASE_CONFIG`: 基础请求配置（请求头、超时时间等）
- `CRAWLER_SETTINGS`: 爬虫设置（最大页数、并发数等）
- `STORAGE_CONFIG`: 数据存储配置（格式、目录等）
- `LOGGING_CONFIG`: 日志配置
- `SELENIUM_CONFIG`: Selenium相关配置

## 使用方法

### 1. 基本使用

```python
from crawler import WebCrawler

# 创建爬虫实例
crawler = WebCrawler()

# 定义选择器（CSS选择器语法）
selectors = {
    'title': 'title',           # 页面标题
    'headings': 'h1, h2, h3',   # 标题标签
    'paragraphs': 'p',          # 段落
    'links': 'a[href]',         # 链接
    'images': 'img',            # 图片
}

# 爬取单个页面
url = "https://example.com"
data = crawler.crawl_single_page(url, selectors)

# 保存数据
if data:
    file_path = crawler.save_data([data], 'json')
    print(f"数据已保存到: {file_path}")
```

### 2. 爬取多个页面

```python
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

results = crawler.crawl_multiple_pages(urls, selectors)

# 保存所有结果
file_path = crawler.save_data(results, 'csv')
```

### 3. 带分页的爬取

```python
# 爬取分页内容，最多10页
results = crawler.crawl_with_pagination(
    base_url="https://example.com/list", 
    selectors=selectors,
    max_pages=10,
    page_param='page'
)
```

### 4. 使用Selenium（处理JavaScript渲染页面）

```python
# 在爬取时启用Selenium
data = crawler.crawl_single_page(url, selectors, use_selenium=True)
```

## 保存格式

支持多种数据保存格式：

- JSON: 适合结构化数据，保留完整信息
- CSV: 适合表格数据，易于Excel打开
- Excel: 适合复杂表格数据

## 注意事项

1. 请遵守网站的robots.txt协议
2. 合理设置请求间隔，避免对目标网站造成过大压力
3. 注意处理异常和错误情况
4. 对于需要登录或有反爬措施的网站，需要额外处理
5. 遵守相关法律法规，合法使用爬虫技术

## 扩展功能

您可以根据需要扩展爬虫功能：

1. 添加代理支持
2. 实现登录认证
3. 添加更复杂的数据解析逻辑
4. 实现增量爬取
5. 添加数据验证功能