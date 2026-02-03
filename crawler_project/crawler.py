import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import re
import json
import os
from utils.logger import crawler_logger
from utils.data_storage import DataStorage
from config import BASE_CONFIG, CRAWLER_SETTINGS, STORAGE_CONFIG, SELENIUM_CONFIG

class WebCrawler:
    """基础网页爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.storage = DataStorage(STORAGE_CONFIG['data_dir'])
        self.visited_urls = set()
        
        # 设置请求头
        self.headers = BASE_CONFIG['headers'].copy()
        
        crawler_logger.info("爬虫初始化完成")
    
    def get_page(self, url, use_selenium=False):
        """获取网页内容"""
        if use_selenium:
            return self._get_with_selenium(url)
        
        # 检查URL是否已访问过
        if url in self.visited_urls:
            crawler_logger.warning(f"URL已访问过: {url}")
            return None
        
        # 添加随机User-Agent
        if CRAWLER_SETTINGS['random_user_agent']:
            self.headers['User-Agent'] = self.ua.random
        
        try:
            # 随机延迟，避免被封
            delay = random.uniform(*BASE_CONFIG['delay_range'])
            time.sleep(delay)
            
            response = self.session.get(
                url, 
                headers=self.headers, 
                timeout=BASE_CONFIG['timeout']
            )
            response.encoding = BASE_CONFIG['encoding']
            
            if response.status_code == 200:
                self.visited_urls.add(url)
                crawler_logger.info(f"成功获取页面: {url}")
                return response
            else:
                crawler_logger.error(f"请求失败，状态码: {response.status_code}, URL: {url}")
                return None
                
        except requests.exceptions.RequestException as e:
            crawler_logger.error(f"请求异常: {e}, URL: {url}")
            return None
    
    def _get_with_selenium(self, url):
        """使用Selenium获取网页内容（用于JavaScript渲染的页面）"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            if SELENIUM_CONFIG.get('headless', True):
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('user-agent=' + self.ua.random)
            
            # 使用webdriver-manager自动管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.implicitly_wait(SELENIUM_CONFIG.get('implicitly_wait', 10))
            driver.get(url)
            
            html = driver.page_source
            driver.quit()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            return type('Response', (), {
                'status_code': 200,
                'text': html,
                'content': html.encode('utf-8'),
                'soup': soup
            })()
            
        except Exception as e:
            crawler_logger.error(f"Selenium请求异常: {e}, URL: {url}")
            return None
    
    def parse_page(self, response, selectors):
        """解析页面内容"""
        if not response:
            return None
        
        # 如果response有soup属性（来自Selenium），则直接使用
        if hasattr(response, 'soup'):
            soup = response.soup
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        
        for field_name, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    # 单个元素
                    if field_name.endswith('_html'):
                        data[field_name] = elements[0].prettify()
                    elif field_name.endswith('_attrs'):
                        data[field_name] = elements[0].attrs
                    else:
                        data[field_name] = elements[0].get_text(strip=True)
                else:
                    # 多个元素
                    if field_name.endswith('_html'):
                        data[field_name] = [elem.prettify() for elem in elements]
                    elif field_name.endswith('_attrs'):
                        data[field_name] = [elem.attrs for elem in elements]
                    else:
                        data[field_name] = [elem.get_text(strip=True) for elem in elements]
            else:
                data[field_name] = None
        
        return data
    
    def extract_links(self, response, link_selector='a[href]'):
        """从页面中提取链接"""
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for link in soup.select(link_selector):
            href = link.get('href')
            if href:
                full_url = urljoin(response.url, href)
                if self.is_valid_url(full_url):
                    links.append(full_url)
        
        return links
    
    def is_valid_url(self, url):
        """检查URL是否有效"""
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme) and parsed.scheme in ['http', 'https']
    
    def extract_images(self, response, img_selector='img'):
        """从页面中提取图片链接"""
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        # 使用response.url，如果没有则使用response.request.url
        base_url = getattr(response, 'url', None) or getattr(response.request, 'url', '')
        
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
            delay = random.uniform(*BASE_CONFIG['delay_range'])
            time.sleep(delay)
            
            # 添加适当的请求头
            headers = self.headers.copy()
            headers['Accept'] = 'image/webp,image/apng,image/*,*/*;q=0.8'
            
            response = self.session.get(img_url, headers=headers, timeout=BASE_CONFIG['timeout'])
            
            if response.status_code == 200:
                # 获取文件扩展名并生成文件名
                parsed_url = urlparse(img_url)
                filename = os.path.basename(parsed_url.path)
                
                # 如果URL中没有文件名，则使用UUID或时间戳
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
                
                crawler_logger.info(f"图片下载成功: {img_url} -> {filepath}")
                return filepath
            else:
                crawler_logger.error(f"图片下载失败，状态码: {response.status_code}, URL: {img_url}")
                return None
                
        except Exception as e:
            crawler_logger.error(f"图片下载异常: {e}, URL: {img_url}")
            return None
    
    def download_images_from_page(self, url, save_dir='images', use_selenium=False):
        """从指定页面下载所有PNG/JPG图片"""
        response = self.get_page(url, use_selenium)
        if not response:
            return []
        
        images = self.extract_images(response)
        downloaded_files = []
        
        for img_info in images:
            img_url = img_info['url']
            crawler_logger.info(f"正在下载图片: {img_url}")
            
            filepath = self.download_image(img_url, save_dir)
            if filepath:
                downloaded_files.append({
                    'url': img_url,
                    'filepath': filepath,
                    'alt': img_info['alt'],
                    'title': img_info['title']
                })
        
        return downloaded_files
    
    def crawl_single_page(self, url, selectors, use_selenium=False):
        """爬取单个页面"""
        response = self.get_page(url, use_selenium)
        if response:
            data = self.parse_page(response, selectors)
            return data
        return None
    
    def crawl_multiple_pages(self, urls, selectors, use_selenium=False):
        """爬取多个页面"""
        results = []
        
        for i, url in enumerate(urls):
            crawler_logger.info(f"正在爬取 ({i+1}/{len(urls)}): {url}")
            data = self.crawl_single_page(url, selectors, use_selenium)
            
            if data:
                data['source_url'] = url
                results.append(data)
        
        return results
    
    def crawl_with_pagination(self, base_url, selectors, max_pages=None, page_param='page', use_selenium=False):
        """带分页的爬取"""
        if max_pages is None:
            max_pages = CRAWLER_SETTINGS['max_pages']
        
        results = []
        
        for page in range(1, max_pages + 1):
            url = f"{base_url}?{page_param}={page}" if '?' in base_url else f"{base_url}?{page_param}={page}"
            crawler_logger.info(f"正在爬取第 {page} 页: {url}")
            
            data = self.crawl_single_page(url, selectors, use_selenium)
            if data:
                data['source_url'] = url
                data['page'] = page
                results.append(data)
            else:
                # 如果某页没有数据，可能已经到达末页，停止爬取
                crawler_logger.info(f"第 {page} 页没有数据，停止爬取")
                break
        
        return results
    
    def save_data(self, data, format_type=None):
        """保存数据"""
        if format_type is None:
            format_type = STORAGE_CONFIG['save_format']
        
        if format_type.lower() == 'json':
            return self.storage.save_to_json(data)
        elif format_type.lower() == 'csv':
            return self.storage.save_to_csv(data)
        elif format_type.lower() == 'excel':
            return self.storage.save_to_excel(data)
        else:
            crawler_logger.warning(f"不支持的保存格式: {format_type}，使用默认JSON格式")
            return self.storage.save_to_json(data)


def main():
    """示例用法"""
    # 创建爬虫实例
    crawler = WebCrawler()
    
    # 定义选择器（根据实际网页结构调整）
    selectors = {
        'title': 'title',  # 页面标题
        'headings': 'h1, h2, h3',  # 标题标签
        'paragraphs': 'p',  # 段落
        'links': 'a[href]',  # 链接
        'images': 'img',  # 图片
    }
    
    # 爬取单个页面示例（使用Selenium）
    url = "https://www.bilibili.com/"  # 示例网站
    data = crawler.crawl_single_page(url, selectors, use_selenium=True)
    
    if data:
        print("爬取的数据:", json.dumps(data, ensure_ascii=False, indent=2))
        
        # 保存数据
        file_path = crawler.save_data([data], 'json')
        crawler_logger.info(f"数据已保存到: {file_path}")
    else:
        crawler_logger.error("未能爬取到数据")

    # 示例：下载页面中的图片
    print("\n开始下载页面中的PNG/JPG图片...")
    image_results = crawler.download_images_from_page(url, save_dir='images', use_selenium=True)
    print(f"共下载了 {len(image_results)} 张图片")


if __name__ == "__main__":
    main()