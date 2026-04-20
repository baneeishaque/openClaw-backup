#!/usr/bin/env python3
"""
微信公众号文章发布脚本
使用方法：
1. 在 config.json 中填入你的 AppID 和 AppSecret
2. 运行: uv run python wechat_publish.py <文章文件路径>
3. 文章会先创建草稿，然后发布
"""

import json
import sys
import os
import requests
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        config = {
            "appid": "",
            "secret": "",
            "author": "",
            "digest": ""
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"⚠️  请先编辑 {CONFIG_FILE} 填入你的 AppID 和 AppSecret")
        sys.exit(1)
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    if not config.get("appid") or not config.get("secret"):
        print("⚠️  请先在 config.json 中填入 AppID 和 AppSecret")
        sys.exit(1)
    
    return config

def get_access_token(appid, secret):
    """获取 access_token"""
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    
    if "access_token" not in data:
        print(f"❌ 获取 access_token 失败: {data}")
        sys.exit(1)
    
    return data["access_token"]

def read_article(file_path):
    """读取文章内容（Markdown格式）"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 从第一行提取标题
    lines = content.strip().split("\n")
    title = lines[0].lstrip("# ").strip() if lines else "无标题"
    
    # 正文（跳过标题行）
    body = "\n".join(lines[1:]).strip()
    
    # 摘取前54个字作为摘要
    plain_text = body.replace("#", "").replace("*", "").replace("\n", " ").strip()
    digest = plain_text[:54] if plain_text else ""
    
    return title, body, digest

def create_draft(access_token, title, content, author="", digest=""):
    """创建草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    article = {
        "title": title,
        "author": author or "",
        "digest": digest or "",
        "content": content,
        "content_source_url": "",
        "need_open_comment": 1,  # 开启评论
        "only_fans_can_comment": 0  # 所有人都能评论
    }
    
    payload = {"articles": [article]}
    
    resp = requests.post(url, json=payload)
    data = resp.json()
    
    if "media_id" not in data:
        print(f"❌ 创建草稿失败: {data}")
        sys.exit(1)
    
    return data["media_id"]

def publish_article(access_token, media_id):
    """发布文章"""
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
    
    payload = {"media_id": media_id}
    
    resp = requests.post(url, json=payload)
    data = resp.json()
    
    if data.get("errcode", 0) != 0:
        print(f"❌ 发布失败: {data}")
        sys.exit(1)
    
    return data.get("publish_id", "")

def main():
    if len(sys.argv) < 2:
        print("用法: uv run python wechat_publish.py <文章文件路径>")
        print("示例: uv run python wechat_publish.py ../articles/断舍离-怎么扔东西不后悔.md")
        sys.exit(1)
    
    article_path = sys.argv[1]
    if not os.path.exists(article_path):
        print(f"❌ 文件不存在: {article_path}")
        sys.exit(1)
    
    # 加载配置
    config = load_config()
    
    # 读取文章
    title, content, auto_digest = read_article(article_path)
    print(f"📝 文章标题: {title}")
    
    # 获取摘要（优先用配置的，否则自动截取）
    digest = config.get("digest") or auto_digest
    
    # 获取 access_token
    print("🔑 获取 access_token...")
    access_token = get_access_token(config["appid"], config["secret"])
    print("✅ access_token 获取成功")
    
    # 创建草稿
    print("📄 创建草稿...")
    media_id = create_draft(
        access_token, 
        title, 
        content,
        author=config.get("author", ""),
        digest=digest
    )
    print(f"✅ 草稿创建成功，media_id: {media_id}")
    
    # 确认发布
    confirm = input("🚀 确认发布？(y/n): ").strip().lower()
    if confirm != "y":
        print("❌ 已取消发布")
        sys.exit(0)
    
    # 发布
    print("🚀 正在发布...")
    publish_id = publish_article(access_token, media_id)
    print(f"✅ 发布成功！publish_id: {publish_id}")
    print("💡 请到公众号后台检查发布状态")

if __name__ == "__main__":
    main()
