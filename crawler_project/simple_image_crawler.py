#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单图片爬虫
仅用于爬取和下载PNG/JPG格式的图片
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import os
import json
from fake_useragent import UserAgent


class SimpleImageCrawler:
    """简单图片爬虫类，专注于图片下载"""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print("简单图片爬虫初始化完成")
    
    def get_page(self, url):
        """获取网页内容"""
        # 添加随机User-Agent
        headers = self.headers.copy()
        headers['User-Agent'] = self.ua.random
        
        try:
            # 随机延迟，避免被封
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=10
            )
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                print(f"成功获取页面: {url}")
                return response
            else:
                print(f"请求失败，状态码: {response.status_code}, URL: {url}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}, URL: {url}")
            return None
    
    def extract_images(self, response, img_selector='img'):
        """从页面中提取图片链接"""
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        # 使用response.request.url作为基础URL
        base_url = response.request.url
        
        for img in soup.select(img_selector):
            src = img.get('src') or img.get('data-src')  # 有些图片使用懒加载，使用data-src
            if src:
                full_url = urljoin(base_url, src)
                # 只包含PNG和JPG格式的图片
                if self.is_image_url(full_url):
                    images.append({
                        'url': full_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
        
        return images
    
    def is_image_url(self, url):
        """检查URL是否为图片链接（PNG/JPG）"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        return path.endswith(('.png', '.jpg', '.jpeg'))
    
    def download_image(self, img_url, save_dir='images'):
        """下载单张图片"""
        # 创建图片保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        try:
            # 随机延时，避免被封
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            # 添加适当的请求头
            headers = self.headers.copy()
            headers['Accept'] = 'image/webp,image/apng,image/*,*/*;q=0.8'
            
            response = self.session.get(img_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 获取文件扩展名并生成文件名
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                
                # 如果URL中没有文件名，则使用时间戳
                if not filename or '.' not in filename:
                    ext = '.jpg'  # 默认扩展名
                    if 'png' in response.headers.get('Content-Type', '').lower():
                        ext = '.png'
                    filename = f"image_{int(time.time())}_{random.randint(1000, 9999)}{ext}"
                
                filepath = os.path.join(save_dir, filename)
                
                # 如果文件已存在，添加数字后缀
                counter = 1
                original_filepath = filepath
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(original_filepath)
                    filepath = f"{name}_{counter}{ext}"
                    counter += 1
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"图片下载成功: {img_url} -> {filepath}")
                return filepath
            else:
                print(f"图片下载失败，状态码: {response.status_code}, URL: {img_url}")
                return None
                
        except Exception as e:
            print(f"图片下载异常: {e}, URL: {img_url}")
            return None
    
    def download_images_from_page(self, url, save_dir='images'):
        """从指定页面下载所有PNG/JPG图片"""
        response = self.get_page(url)
        if not response:
            return []
        
        images = self.extract_images(response)
        downloaded_files = []
        
        print(f"找到 {len(images)} 个图片链接")
        
        for i, img_info in enumerate(images):
            img_url = img_info['url']
            print(f"正在下载图片 {i+1}/{len(images)}: {img_url}")
            
            filepath = self.download_image(img_url, save_dir)
            if filepath:
                downloaded_files.append({
                    'url': img_url,
                    'filepath': filepath,
                    'alt': img_info['alt'],
                    'title': img_info['title']
                })
        
        return downloaded_files


def main():
    """主函数 - 图片爬取示例"""
    # 创建爬虫实例
    crawler = SimpleImageCrawler()
    
    # 示例：爬取一个网站的图片
    url = input("请输入要爬取图片的网址 (例如 https://www.baidu.com): ").strip()
    if not url:
        url = "https://www.baidu.com"  # 默认示例
    
    print(f"\n开始从 {url} 爬取PNG/JPG图片...")
    results = crawler.download_images_from_page(url, save_dir='images')
    
    print(f"\n爬取完成！总共下载了 {len(results)} 张图片")
    
    if results:
        print("\n下载的图片列表:")
        for i, img_info in enumerate(results, 1):
            print(f"  {i}. {img_info['filepath']} - {img_info['url']}")
    
    # 保存结果到JSON文件
    if results:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"image_scraping_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到 {filename}")


if __name__ == "__main__":
    main()