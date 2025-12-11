"""
JSON 加载器使用示例
演示如何使用 JsonLoader 从不同来源加载 JSON 数据
"""

from json_loader import JsonLoader, JsonLoaderError, load_json_from_file, load_json_from_string, load_json_from_url
import os


def example_load_from_string():
    """示例：从字符串加载 JSON"""
    print("\n" + "=" * 60)
    print("示例 1: 从字符串加载 JSON")
    print("=" * 60)
    
    loader = JsonLoader()
    
    # 示例 JSON 字符串
    json_str = '''
    {
        "name": "张三",
        "age": 30,
        "city": "北京",
        "hobbies": ["阅读", "编程", "旅行"],
        "is_student": false
    }
    '''
    
    try:
        data = loader.load_from_string(json_str)
        print("✓ JSON 加载成功！")
        print("\n格式化输出：")
        print(loader.pretty_print(data))
        
        # 验证数据
        if loader.validate_json(data):
            print("\n✓ JSON 数据验证通过")
        
    except JsonLoaderError as e:
        print(f"✗ 错误: {e}")


def example_load_from_file():
    """示例：从文件加载 JSON"""
    print("\n" + "=" * 60)
    print("示例 2: 从文件加载 JSON")
    print("=" * 60)
    
    loader = JsonLoader()
    
    # 创建一个示例 JSON 文件
    sample_data = {
        "project": "JSON 加载器",
        "version": "1.0.0",
        "author": "开发者",
        "features": [
            "从文件加载",
            "从字符串加载",
            "从 URL 加载",
            "数据验证",
            "格式化输出"
        ],
        "config": {
            "timeout": 10,
            "encoding": "utf-8"
        }
    }
    
    # 保存示例文件
    sample_file = "sample_data.json"
    try:
        loader.save_to_file(sample_data, sample_file)
        print(f"✓ 已创建示例文件: {sample_file}")
        
        # 从文件加载
        loaded_data = loader.load_from_file(sample_file)
        print("✓ 从文件加载成功！")
        print("\n加载的数据：")
        print(loader.pretty_print(loaded_data))
        
    except JsonLoaderError as e:
        print(f"✗ 错误: {e}")
    finally:
        # 清理示例文件
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print(f"\n✓ 已清理示例文件: {sample_file}")


def example_load_from_url():
    """示例：从 URL 加载 JSON"""
    print("\n" + "=" * 60)
    print("示例 3: 从 URL 加载 JSON")
    print("=" * 60)
    
    loader = JsonLoader()
    
    # 使用一个公开的 JSON API 测试
    test_url = "https://jsonplaceholder.typicode.com/posts/1"
    
    try:
        print(f"正在从 URL 加载: {test_url}")
        data = loader.load_from_url(test_url, timeout=10)
        print("✓ 从 URL 加载成功！")
        print("\n加载的数据：")
        print(loader.pretty_print(data, indent=2))
        
    except JsonLoaderError as e:
        print(f"✗ 错误: {e}")
        print("提示: 如果网络不可用，此示例会失败")


def example_error_handling():
    """示例：错误处理"""
    print("\n" + "=" * 60)
    print("示例 4: 错误处理演示")
    print("=" * 60)
    
    loader = JsonLoader()
    
    # 测试无效的 JSON 字符串
    print("\n1. 测试无效的 JSON 字符串:")
    try:
        invalid_json = "{'name': 'test', 'invalid': }"
        loader.load_from_string(invalid_json)
    except JsonLoaderError as e:
        print(f"   ✓ 正确捕获错误: {e}")
    
    # 测试不存在的文件
    print("\n2. 测试不存在的文件:")
    try:
        loader.load_from_file("nonexistent_file.json")
    except JsonLoaderError as e:
        print(f"   ✓ 正确捕获错误: {e}")
    
    # 测试无效的 URL
    print("\n3. 测试无效的 URL:")
    try:
        loader.load_from_url("not-a-valid-url")
    except JsonLoaderError as e:
        print(f"   ✓ 正确捕获错误: {e}")


def example_convenience_functions():
    """示例：使用便捷函数"""
    print("\n" + "=" * 60)
    print("示例 5: 使用便捷函数")
    print("=" * 60)
    
    # 使用便捷函数加载 JSON
    json_str = '{"message": "Hello, World!", "count": 42}'
    
    try:
        # 使用便捷函数
        data = load_json_from_string(json_str)
        print("✓ 使用便捷函数加载成功！")
        print(f"数据: {data}")
        
    except JsonLoaderError as e:
        print(f"✗ 错误: {e}")


def example_save_and_load():
    """示例：保存和加载 JSON 文件"""
    print("\n" + "=" * 60)
    print("示例 6: 保存和加载 JSON 文件")
    print("=" * 60)
    
    loader = JsonLoader()
    
    # 创建复杂的数据结构
    complex_data = {
        "users": [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "roles": ["admin", "user"]
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "roles": ["user"]
            }
        ],
        "settings": {
            "theme": "dark",
            "language": "zh-CN",
            "notifications": True
        },
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "version": "1.0"
        }
    }
    
    file_path = "example_output.json"
    
    try:
        # 保存数据
        loader.save_to_file(complex_data, file_path)
        print(f"✓ 数据已保存到: {file_path}")
        
        # 重新加载数据
        loaded_data = loader.load_from_file(file_path)
        print("✓ 数据加载成功！")
        
        # 验证数据一致性
        if loaded_data == complex_data:
            print("✓ 数据验证通过：保存和加载的数据一致")
        
        # 显示格式化输出
        print("\n格式化输出：")
        print(loader.pretty_print(loaded_data))
        
    except JsonLoaderError as e:
        print(f"✗ 错误: {e}")
    finally:
        # 清理文件
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"\n✓ 已清理文件: {file_path}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("JSON 加载器使用示例")
    print("=" * 60)
    
    # 运行所有示例
    example_load_from_string()
    example_load_from_file()
    example_load_from_url()
    example_error_handling()
    example_convenience_functions()
    example_save_and_load()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

