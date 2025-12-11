"""
Python JSON 加载器模块
支持从文件、字符串、URL 等多种来源加载 JSON 数据
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse


class JsonLoaderError(Exception):
    """JSON 加载器自定义异常"""
    pass


class JsonLoader:
    """JSON 数据加载器类"""
    
    def __init__(self):
        """初始化 JSON 加载器"""
        pass
    
    def load_from_file(self, file_path: str, encoding: str = 'utf-8') -> Union[Dict, List, Any]:
        """
        从文件加载 JSON 数据
        
        Args:
            file_path: JSON 文件路径
            encoding: 文件编码，默认为 'utf-8'
            
        Returns:
            解析后的 JSON 数据（字典、列表或其他类型）
            
        Raises:
            JsonLoaderError: 当文件不存在、无法读取或 JSON 解析失败时抛出
        """
        if not os.path.exists(file_path):
            raise JsonLoaderError(f"文件不存在: {file_path}")
        
        if not os.path.isfile(file_path):
            raise JsonLoaderError(f"路径不是文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                return self.load_from_string(content)
        except UnicodeDecodeError as e:
            raise JsonLoaderError(f"文件编码错误 ({encoding}): {file_path} - {str(e)}")
        except IOError as e:
            raise JsonLoaderError(f"文件读取错误: {file_path} - {str(e)}")
    
    def load_from_string(self, json_str: str) -> Union[Dict, List, Any]:
        """
        从字符串加载 JSON 数据
        
        Args:
            json_str: JSON 格式的字符串
            
        Returns:
            解析后的 JSON 数据（字典、列表或其他类型）
            
        Raises:
            JsonLoaderError: 当 JSON 字符串格式错误时抛出
        """
        if not json_str or not json_str.strip():
            raise JsonLoaderError("JSON 字符串为空")
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise JsonLoaderError(f"JSON 解析错误: {str(e)}")
    
    def load_from_url(self, url: str, timeout: int = 10, headers: Optional[Dict[str, str]] = None) -> Union[Dict, List, Any]:
        """
        从 URL 加载 JSON 数据
        
        Args:
            url: JSON 数据的 URL 地址
            timeout: 请求超时时间（秒），默认为 10
            headers: 可选的 HTTP 请求头字典
            
        Returns:
            解析后的 JSON 数据（字典、列表或其他类型）
            
        Raises:
            JsonLoaderError: 当网络请求失败或 JSON 解析失败时抛出
        """
        if not url:
            raise JsonLoaderError("URL 不能为空")
        
        # 验证 URL 格式
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise JsonLoaderError(f"无效的 URL 格式: {url}")
        
        try:
            # 创建请求对象
            req = Request(url)
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            # 发送请求
            with urlopen(req, timeout=timeout) as response:
                # 检查响应状态码
                if response.status != 200:
                    raise JsonLoaderError(f"HTTP 错误: 状态码 {response.status}")
                
                # 读取响应内容
                content = response.read()
                
                # 尝试检测编码
                encoding = response.headers.get_content_charset() or 'utf-8'
                
                # 解码内容
                json_str = content.decode(encoding)
                
                # 解析 JSON
                return self.load_from_string(json_str)
                
        except HTTPError as e:
            raise JsonLoaderError(f"HTTP 请求错误: {url} - {str(e)}")
        except URLError as e:
            raise JsonLoaderError(f"URL 请求错误: {url} - {str(e)}")
        except TimeoutError:
            raise JsonLoaderError(f"请求超时: {url} (超时时间: {timeout}秒)")
        except Exception as e:
            raise JsonLoaderError(f"未知错误: {url} - {str(e)}")
    
    def validate_json(self, data: Any) -> bool:
        """
        验证数据是否为有效的 JSON 结构
        
        Args:
            data: 要验证的数据
            
        Returns:
            如果数据是有效的 JSON 结构（字典、列表、字符串、数字、布尔值、None），返回 True
        """
        if data is None:
            return True
        
        if isinstance(data, (dict, list, str, int, float, bool)):
            if isinstance(data, dict):
                return all(self.validate_json(v) for v in data.values())
            elif isinstance(data, list):
                return all(self.validate_json(item) for item in data)
            else:
                return True
        
        return False
    
    def pretty_print(self, data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        格式化输出 JSON 数据
        
        Args:
            data: 要格式化的 JSON 数据
            indent: 缩进空格数，默认为 2
            ensure_ascii: 是否确保 ASCII 编码，默认为 False（支持中文）
            
        Returns:
            格式化后的 JSON 字符串
        """
        try:
            return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, sort_keys=False)
        except TypeError as e:
            raise JsonLoaderError(f"无法序列化数据: {str(e)}")
    
    def save_to_file(self, data: Any, file_path: str, encoding: str = 'utf-8', 
                     indent: int = 2, ensure_ascii: bool = False) -> None:
        """
        将 JSON 数据保存到文件
        
        Args:
            data: 要保存的 JSON 数据
            file_path: 保存的文件路径
            encoding: 文件编码，默认为 'utf-8'
            indent: 缩进空格数，默认为 2
            ensure_ascii: 是否确保 ASCII 编码，默认为 False
            
        Raises:
            JsonLoaderError: 当文件写入失败时抛出
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # 格式化并保存
            formatted_json = self.pretty_print(data, indent=indent, ensure_ascii=ensure_ascii)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(formatted_json)
                
        except IOError as e:
            raise JsonLoaderError(f"文件写入错误: {file_path} - {str(e)}")
        except Exception as e:
            raise JsonLoaderError(f"保存文件时发生错误: {file_path} - {str(e)}")


# 便捷函数
def load_json_from_file(file_path: str, encoding: str = 'utf-8') -> Union[Dict, List, Any]:
    """从文件加载 JSON 的便捷函数"""
    loader = JsonLoader()
    return loader.load_from_file(file_path, encoding)


def load_json_from_string(json_str: str) -> Union[Dict, List, Any]:
    """从字符串加载 JSON 的便捷函数"""
    loader = JsonLoader()
    return loader.load_from_string(json_str)


def load_json_from_url(url: str, timeout: int = 10, headers: Optional[Dict[str, str]] = None) -> Union[Dict, List, Any]:
    """从 URL 加载 JSON 的便捷函数"""
    loader = JsonLoader()
    return loader.load_from_url(url, timeout, headers)

