import json
import csv
import pandas as pd
from datetime import datetime
import os

class DataStorage:
    """数据存储类，支持多种数据格式存储"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        # 创建数据目录（如果不存在）
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_to_json(self, data, filename=None):
        """保存数据到JSON文件"""
        if filename is None:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到 {filepath}")
        return filepath
    
    def save_to_csv(self, data, filename=None, headers=None):
        """保存数据到CSV文件"""
        if filename is None:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        # 如果数据是字典列表，使用pandas保存
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')  # 使用utf-8-sig避免中文乱码
        else:
            # 如果是其他格式，直接写入CSV
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, list) or isinstance(row, tuple):
                            writer.writerow(row)
                        else:
                            writer.writerow([row])
                else:
                    writer.writerow([data])
        
        print(f"数据已保存到 {filepath}")
        return filepath
    
    def save_to_excel(self, data, filename=None):
        """保存数据到Excel文件"""
        if filename is None:
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.data_dir, filename)
        
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data)
        
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        print(f"数据已保存到 {filepath}")
        return filepath