import logging
import os
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    # 创建logs目录（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 创建格式化的日志文件名
    log_filename = os.path.join('logs', f"{log_file}_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 创建logger
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_filename, encoding='utf-8')
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建爬虫日志记录器
crawler_logger = setup_logger('crawler', 'crawler')