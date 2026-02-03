#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片爬虫示例
此脚本演示如何使用爬虫抓取和下载PNG/JPG格式的图片
"""

from crawler import WebCrawler
import json


def crawl_images_example():#只爬取单个网站改这里
    """图片爬取示例"""
    # 创建爬虫实例
    crawler = WebCrawler()
    
    # 目标网址（可以根据需要更改）
    url = "https://www.baidu.com"  # 替换为您想要爬取的网站
    
    print(f"开始从 {url} 爬取PNG/JPG图片...")
    
    # 方法1: 提取页面中的图片链接
    response = crawler.get_page(url, use_selenium=True)
    if response:
        images = crawler.extract_images(response)
        print(f"找到 {len(images)} 个图片链接:")
        for i, img in enumerate(images[:5]):  # 只显示前5个
            print(f"  {i+1}. {img['url']} (alt: {img['alt']})")
        
        # 方法2: 直接下载图片
        print("\n开始下载图片...")
        downloaded_images = crawler.download_images_from_page(url, save_dir='images', use_selenium=True)
        print(f"成功下载 {len(downloaded_images)} 张图片")
        
        for img_info in downloaded_images:
            print(f"  - {img_info['url']} -> {img_info['filepath']}")
    else:
        print("无法获取页面内容")


def crawl_specific_website():#多个网站改这里
    """针对特定网站的图片爬取示例"""
    crawler = WebCrawler()
    
    # 这里以一个示例网站为例，您可以替换为任何您想爬取的网站
    websites = [
        "https://www.baidu.com",  # 百度首页
        # 添加更多网站...
    ]
    
    for website in websites:
        print(f"\n正在处理网站: {website}")
        try:
            results = crawler.download_images_from_page(website, save_dir='images', use_selenium=True)
            print(f"从 {website} 成功下载了 {len(results)} 张图片")
        except Exception as e:
            print(f"处理 {website} 时出错: {str(e)}")


if __name__ == "__main__":
    print("=== PNG/JPG 图片爬取示例 ===")
    
    # 运行示例
    crawl_images_example()
    
    # 或者爬取特定网站
    # crawl_specific_website()