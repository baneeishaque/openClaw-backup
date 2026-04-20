import hashlib

# 你的示例参数
app_key = "123456"
app_secret = "abcdefg123"
body = {"order_id": "20170301000001"}
timestamp = "1488363493"
version = "1.0"

# 第一步：构建参数并排序
import json
params = {
    "appKey": app_key,
    "body": json.dumps(body, separators=(',', ':'), ensure_ascii=False),
    "timestamp": timestamp,
    "version": version
}

print("【第一步】构建参数并字典排序")
print(f"原始参数: {params}")
sorted_keys = sorted(params.keys())
print(f"排序结果: {' → '.join(sorted_keys)}")

# 第二步：拼接参数
print("\n【第二步】拼接key和value")
concat_str = ""
for key in sorted_keys:
    concat_str += f"{key}{params[key]}"
print(f"拼接结果: {concat_str}")

# 第三步：添加秘钥
print("\n【第三步】首尾添加appSecret")
sign_str = f"{app_secret}{concat_str}{app_secret}"
print(f"签名字符串: {sign_str}")

# 第四步：MD5加密
print("\n【第四步】MD5加密")
signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
print(f"最终签名 (32位): {signature}")

print(f"签名长度: {len(signature)} 位")

# 验证（如果你想测试不同的参数）
print("\n" + "="*60)
print("你可以用在线MD5工具验证这个结果：")
print("1. 打开在线MD5工具网站")
print("2. 输入字符串：")
print(f"   {sign_str}")
print("3. 应该得到相同的MD5值：")
print(f"   {signature}")