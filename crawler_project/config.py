# 爬虫配置文件

# 基本配置
BASE_CONFIG = {
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    },
    'timeout': 10,  # 请求超时时间（秒）
    'delay_range': (1, 3),  # 请求间隔时间范围（秒）
    'max_retries': 3,  # 最大重试次数
    'encoding': 'utf-8',  # 默认编码
}

# 爬虫设置
CRAWLER_SETTINGS = {
    'max_pages': 10,  # 最大爬取页数
    'concurrent_requests': 1,  # 并发请求数
    'respect_robots_txt': True,  # 是否遵守robots.txt
    'download_delay': 1,  # 下载延迟（秒）
    'random_user_agent': True,  # 是否使用随机User-Agent
}

# 数据存储配置
STORAGE_CONFIG = {
    'save_format': 'json',  # 默认保存格式: json, csv, excel
    'data_dir': 'data',  # 数据存储目录
    'filename_prefix': 'scraped_data',  # 文件名前缀
}

# 日志配置
LOGGING_CONFIG = {
    'log_level': 'INFO',  # 日志级别
    'log_dir': 'logs',  # 日志存储目录
    'log_file_max_bytes': 10 * 1024 * 1024,  # 单个日志文件最大大小（10MB）
    'backup_count': 5,  # 保留的备份日志文件数量
}

# Selenium配置（如果使用）
SELENIUM_CONFIG = {
    'use_selenium': True,  # 是否使用Selenium
    'driver_path': '',  # WebDriver路径
    'headless': True,  # 是否使用无头模式
    'implicitly_wait': 5,  # 隐式等待时间（秒）
}