"""
API签名工具类
支持字典排序、参数拼接、MD5加密生成签名
"""

import hashlib
from typing import Dict, Any, Optional


class SignatureGenerator:
    """API签名生成器"""
    
    def __init__(self, app_key: str, app_secret: str):
        """
        初始化签名生成器
        
        Args:
            app_key: 应用key
            app_secret: 应用密钥
        """
        self.app_key = app_key
        self.app_secret = app_secret
    
    def generate_signature(
        self, 
        body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        version: str = "1.0",
        extra_params: Optional[Dict[str, str]] = None
    ) -> str:
        """
        生成API签名
        
        Args:
            body: 请求体数据（字典格式）
            timestamp: 时间戳（可选，不传则自动生成）
            version: 版本号，默认1.0
            extra_params: 额外的请求参数
        
        Returns:
            32位MD5签名字符串
        """
        import json
        import time
        
        # 构建参数字典
        params = {
            "appKey": self.app_key,
            "version": version
        }
        
        # 添加body参数
        if body is not None:
            params["body"] = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
        
        # 添加时间戳
        if timestamp is None:
            timestamp = str(int(time.time()))
        params["timestamp"] = timestamp
        
        # 添加额外参数
        if extra_params:
            params.update(extra_params)
        
        # 第一步：字典排序
        sorted_keys = sorted(params.keys())
        
        # 第二步：拼接key和value
        concat_str = ""
        for key in sorted_keys:
            concat_str += f"{key}{params[key]}"
        
        # 第三步：首尾加上appSecret
        sign_str = f"{self.app_secret}{concat_str}{self.app_secret}"
        
        # 第四步：MD5加密
        md5_hash = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        return md5_hash
    
    def verify_signature(
        self,
        signature: str,
        body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        version: str = "1.0",
        extra_params: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        验证签名是否正确
        
        Args:
            signature: 待验证的签名
            其他参数同generate_signature
        
        Returns:
            签名是否匹配
        """
        generated = self.generate_signature(body, timestamp, version, extra_params)
        return generated.lower() == signature.lower()


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例参数（根据你的描述）
    app_key = "123456"
    app_secret = "abcdefg123"
    
    # 创建签名生成器
    signer = SignatureGenerator(app_key, app_secret)
    
    # 示例1：基本用法
    body_data = {"order_id": "20170301000001"}
    timestamp = "1488363493"
    
    signature = signer.generate_signature(
        body=body_data,
        timestamp=timestamp,
        version="1.0"
    )
    
    print("=" * 50)
    print("签名生成示例")
    print("=" * 50)
    print(f"App Key: {app_key}")
    print(f"App Secret: {app_secret}")
    print(f"Body: {body_data}")
    print(f"Timestamp: {timestamp}")
    print(f"Version: 1.0")
    print("-" * 50)
    print(f"生成的签名: {signature}")
    print("=" * 50)
    
    # 验证签名
    is_valid = signer.verify_signature(signature, body_data, timestamp, "1.0")
    print(f"签名验证结果: {'✓ 通过' if is_valid else '✗ 失败'}")
    
    # 示例2：自动生成时间戳
    print("\n" + "=" * 50)
    print("自动生成时间戳示例")
    print("=" * 50)
    signature_auto = signer.generate_signature(body={"order_id": "20260331001"})
    print(f"自动时间戳签名: {signature_auto}")
    
    # 示例3：添加额外参数
    print("\n" + "=" * 50)
    print("额外参数示例")
    print("=" * 50)
    signature_extra = signer.generate_signature(
        body={"order_id": "20260331002"},
        extra_params={"device": "mobile", "channel": "web"}
    )
    print(f"带额外参数签名: {signature_extra}")


# ==================== 工具函数（可单独调用）====================

def sort_params(params: Dict[str, str]) -> list:
    """
    第一步：字典排序
    
    Args:
        params: 参数字典
    
    Returns:
        排序后的key列表
    """
    return sorted(params.keys())


def concat_params(params: Dict[str, str], sorted_keys: list) -> str:
    """
    第二步：拼接参数
    
    Args:
        params: 参数字典
        sorted_keys: 排序后的key列表
    
    Returns:
        拼接后的字符串
    """
    result = ""
    for key in sorted_keys:
        result += f"{key}{params[key]}"
    return result


def add_secret(concat_str: str, app_secret: str) -> str:
    """
    第三步：添加秘钥
    
    Args:
        concat_str: 拼接后的字符串
        app_secret: 应用秘钥
    
    Returns:
        添加秘钥后的字符串
    """
    return f"{app_secret}{concat_str}{app_secret}"


def md5_encrypt(text: str) -> str:
    """
    第四步：MD5加密
    
    Args:
        text: 待加密字符串
    
    Returns:
        32位MD5字符串
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


# ==================== 完整流程演示 ====================

def demo_full_process():
    """完整签名流程演示"""
    print("\n" + "=" * 60)
    print("完整签名生成流程演示")
    print("=" * 60)
    
    # 参数设置
    app_key = "123456"
    app_secret = "abcdefg123"
    body = {"order_id": "20170301000001"}
    timestamp = "1488363493"
    version = "1.0"
    
    import json
    
    # 第一步：构建参数并排序
    params = {
        "appKey": app_key,
        "body": json.dumps(body, separators=(',', ':'), ensure_ascii=False),
        "timestamp": timestamp,
        "version": version
    }
    
    print("\n【第一步】构建参数并字典排序")
    print(f"原始参数: {params}")
    sorted_keys = sort_params(params)
    print(f"排序结果: {' → '.join(sorted_keys)}")
    
    # 第二步：拼接参数
    print("\n【第二步】拼接key和value")
    concat_str = concat_params(params, sorted_keys)
    print(f"拼接结果: {concat_str}")
    
    # 第三步：添加秘钥
    print("\n【第三步】首尾添加appSecret")
    sign_str = add_secret(concat_str, app_secret)
    print(f"签名字符串: {sign_str}")
    
    # 第四步：MD5加密
    print("\n【第四步】MD5加密")
    signature = md5_encrypt(sign_str)
    print(f"最终签名: {signature}")
    
    print("\n" + "=" * 60)
    
    return signature


if __name__ == "__main__":
    demo_full_process()