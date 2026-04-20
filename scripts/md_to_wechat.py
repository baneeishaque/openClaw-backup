#!/usr/bin/env python3
"""
Markdown 转微信公众号 HTML
使用方法：uv run python md_to_wechat.py <文章文件路径>
生成的 HTML 可以直接复制粘贴到微信公众号后台编辑器
"""

import sys
import re
import os

def md_to_wechat_html(md_content, title=""):
    """将Markdown转换为微信公众号友好的HTML"""
    
    lines = md_content.strip().split("\n")
    
    # 提取标题
    if not title and lines and lines[0].startswith("#"):
        title = lines[0].lstrip("#").strip()
        lines = lines[1:]
    
    html_parts = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # 空行
        if not line:
            i += 1
            continue
        
        # 标题
        if line.startswith("### "):
            text = line[4:].strip()
            html_parts.append(f'<h3 style="font-size: 18px; font-weight: bold; color: #333; margin: 30px 0 15px 0; padding-left: 12px; border-left: 4px solid #2b78e4;">{text}</h3>')
            i += 1
            continue
        elif line.startswith("## "):
            text = line[3:].strip()
            html_parts.append(f'<h2 style="font-size: 20px; font-weight: bold; color: #333; margin: 35px 0 15px 0; padding: 10px 15px; background: linear-gradient(90deg, #f0f7ff 0%, transparent 100%); border-left: 4px solid #2b78e4;">{text}</h2>')
            i += 1
            continue
        elif line.startswith("# "):
            text = line[2:].strip()
            html_parts.append(f'<h1 style="font-size: 24px; font-weight: bold; color: #1a1a1a; margin: 20px 0 30px 0; text-align: center; line-height: 1.4;">{text}</h1>')
            i += 1
            continue
        
        # 分割线
        if line in ["---", "***", "___"]:
            html_parts.append('<hr style="border: none; border-top: 1px solid #e8e8e8; margin: 30px 0;">')
            i += 1
            continue
        
        # 引用块（多行）
        if line.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            quote_text = "<br>".join(quote_lines)
            html_parts.append(f'<blockquote style="margin: 20px 0; padding: 15px 20px; background: #f9f9f9; border-left: 4px solid #2b78e4; color: #666; font-size: 15px; line-height: 1.8;">{quote_text}</blockquote>')
            continue
        
        # 代码块
        if line.startswith("```"):
            code_lines = []
            i += 1  # 跳过开始的 ```
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束的 ```
            code_text = "\n".join(code_lines)
            code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_parts.append(f'<pre style="background: #f6f8fa; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: Consolas, Monaco, monospace; font-size: 13px; line-height: 1.6; color: #333; margin: 20px 0;"><code>{code_text}</code></pre>')
            continue
        
        # 列表项
        if line.startswith("- ") or line.startswith("* "):
            list_items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                item_text = lines[i].strip()[2:].strip()
                item_text = process_inline_formatting(item_text)
                list_items.append(f'<li style="margin: 8px 0; padding-left: 8px; line-height: 1.8;">{item_text}</li>')
                i += 1
            html_parts.append(f'<ul style="margin: 15px 0; padding-left: 20px; color: #333; font-size: 15px;">{"".join(list_items)}</ul>')
            continue
        
        # 有序列表
        ordered_match = re.match(r'^(\d+)\.\s', line)
        if ordered_match:
            list_items = []
            while i < len(lines):
                match = re.match(r'^(\d+)\.\s(.*)', lines[i].strip())
                if not match:
                    break
                item_text = match.group(2).strip()
                item_text = process_inline_formatting(item_text)
                list_items.append(f'<li style="margin: 8px 0; padding-left: 8px; line-height: 1.8;">{item_text}</li>')
                i += 1
            html_parts.append(f'<ol style="margin: 15px 0; padding-left: 20px; color: #333; font-size: 15px;">{"".join(list_items)}</ol>')
            continue
        
        # 普通段落
        paragraph_lines = []
        while i < len(lines) and lines[i].strip() and not any([
            lines[i].strip().startswith("#"),
            lines[i].strip().startswith(">"),
            lines[i].strip().startswith("```"),
            lines[i].strip().startswith("- "),
            lines[i].strip().startswith("* "),
            lines[i].strip() in ["---", "***", "___"],
            re.match(r'^(\d+)\.\s', lines[i].strip())
        ]):
            paragraph_lines.append(lines[i].strip())
            i += 1
        
        if paragraph_lines:
            para_text = " ".join(paragraph_lines)
            para_text = process_inline_formatting(para_text)
            html_parts.append(f'<p style="margin: 15px 0; line-height: 1.8; color: #333; font-size: 15px; text-indent: 0;">{para_text}</p>')
    
    return "\n".join(html_parts)

def process_inline_formatting(text):
    """处理行内格式"""
    # 粗体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #1a1a1a; font-weight: bold;">\1</strong>', text)
    # 斜体
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # 行内代码
    text = re.sub(r'`(.+?)`', r'<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: Consolas, Monaco, monospace; font-size: 14px; color: #e74c3c;">\1</code>', text)
    # 链接
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color: #2b78e4; text-decoration: none;">\1</a>', text)
    
    return text

def main():
    if len(sys.argv) < 2:
        print("用法: uv run python md_to_wechat.py <文章文件路径>")
        print("示例: uv run python md_to_wechat.py ../articles/断舍离-怎么扔东西不后悔.md")
        sys.exit(1)
    
    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"❌ 文件不存在: {md_path}")
        sys.exit(1)
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    html_content = md_to_wechat_html(md_content)
    
    # 生成完整HTML文件（用于预览）
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章预览</title>
    <style>
        body {{
            max-width: 677px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    # 输出HTML文件
    output_path = md_path.replace(".md", "_wechat.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    print(f"✅ 微信公众号 HTML 已生成: {output_path}")
    print()
    print("📋 使用方法:")
    print("1. 用浏览器打开生成的 HTML 文件预览效果")
    print("2. 复制浏览器中的内容")
    print("3. 粘贴到微信公众号后台编辑器")
    print()
    print("💡 提示:")
    print("- 封面图和摘要需要在后台手动设置")
    print("- 如需调整样式，直接修改 md_to_wechat.py 中的样式定义")

if __name__ == "__main__":
    main()
