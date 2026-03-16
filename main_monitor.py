import requests
import json
import logging
import hashlib
import os
import sys
import subprocess
import time
import socket
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
from playwright.sync_api import sync_playwright 

# 导入自定义模块
import config
import utils_email
import utils_ai

# 屏蔽 SSL 警告
urllib3.disable_warnings()

# ================= 配置区 =================
SITE_TIMEOUT = 120   
MIN_IMG_SIZE = 1024 
# =========================================

logging.basicConfig(
    filename=config.LOG_FILE, 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def verify_ai_health():
    print(">>> [系统] 正在连接 AI 算力中心...")
    try:
        ok, _ = utils_ai.analyze_content("hi")
        return ok
    except: return False

def get_dynamic_resources(url):
    """
    核心优化：使用系统自带 Edge 浏览器进行 F12 级别的资源监听
    """
    captured_images = set()
    img_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif')
    rendered_html = ""

    print(f"    ├─ [内核] 正在调用系统 Edge 监控资源... ", end="", flush=True)
    
    with sync_playwright() as p:
        try:
            # 【关键修改】：使用 channel="msedge" 调用 Windows 自带的 Edge
            # 这样即使 playwright install 失败，只要你电脑有 Edge 就能跑
            browser = p.chromium.launch(headless=True, channel="msedge")
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            def capture_response(response):
                ctype = response.headers.get("content-type", "").lower()
                if "image" in ctype or any(ext in response.url.lower() for ext in img_extensions):
                    captured_images.add(response.url)

            page.on("response", capture_response)
            page.goto(url, timeout=60000, wait_until="networkidle")
            
            # 模拟滚动触发懒加载
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000) 
            
            rendered_html = page.content()
            browser.close()
            print(f"成功 (监测到 {len(captured_images)} 个资源) ✅")
        except Exception as e:
            print(f"失败 ❌ ({str(e)})")
            
    return list(captured_images), rendered_html

def check_site(url):
    print(f"Testing: {url}")
    start_time = time.time()
    risks = []
    
    # 1. 动态获取资源
    valid_imgs, content = get_dynamic_resources(url)
    if not content:
        return [f"浏览器引擎访问失败"]

    soup = BeautifulSoup(content, 'html.parser')
    
    # === 2. 文本审计 (完整保留原 Prompt) ===
    full_text = soup.get_text(separator=' ', strip=True)
    audit_text = full_text[:10000]
    print(f"    ├─ [文本] 正在审计... ", end="", flush=True)
    
    prompt_text = f"""
    【角色】：你是一名严格的企业网站安全审计员。
    【背景】：你正在审查一个商业公司的官方网站内容，目的是发现网页是否被黑客篡改或植入恶意内容。
    【任务】：审查以下文本，判断是否存在与正常商业经营无关的“异常内容”。
    【违规判定标准 (零容忍)】：
    1. 涉政敏感类（黑客常见恶意篡改）
    出现与业务无关的敏感国家/地区、敏感政权、分裂言论、涉疆涉藏涉港涉台等违规内容;
    政治谣言、反动言论、煽动性文字、违规政治口号、抹黑国家/党政/社会的内容;
    违规使用、篡改、侮辱国旗、国徽、国歌等国家象征
    2. 违法违规内容类（黑产常见植入）
    色情、招嫖、低俗色情诱导、淫秽相关文字;
    博彩、网络赌博、赌球、棋牌作弊、网赌导流;
    网络诈骗、刷单、传销、非法集资、贷款诈骗、中奖诈骗;
    3. 黑客篡改 / 恶意植入类
    暗链 / 恶意链接; 信息篡改; 恶意代码相关; 隐藏文字; 异常弹窗; 仿冒官方信息;
    4. 无关垃圾 / 导流类
    与企业业务完全无关的广告、微商、导流、非官方收款码。
    【正常内容】：企业业务介绍、新闻、合规公告、官方联系方式、美国/中国台湾等国家或地区或经济体、+886区号等等，"强制刷新页面"等网页刷新提示、全球地图、国内城市、国际、USA/CHINA等国家英文名称、中华人民共和国国徽、中国、"涉密不上网、上网不涉密。手机不拍密、微信不传密、403 Forbidden、国徽、中国交建、台湾省、上海国际集团"等上网提示。
    【回复格式】：安全回复：【安全】，发现异常回复：【违规】+具体发现的异常词汇或句子。
    待审文本：{audit_text}
    """
    
    ok, ai_res = utils_ai.analyze_content(prompt_text)
    if ok and "【安全】" not in ai_res:
        print("🚫 发现异常")
        risks.append(f"[文本异常] {ai_res}")
    else: print("🟢 安全")

    # === 3. 图片审计 (使用监测到的 F12 资源) ===
    total_imgs = len(valid_imgs)
    img_risk_count = 0
    for i, img_url in enumerate(valid_imgs):
        if time.time() - start_time > SITE_TIMEOUT: break
        sys.stdout.write(f"\r    └─ [图片] 正在审计进度 {i+1}/{total_imgs} ")
        sys.stdout.flush()

        try:
            ir = requests.get(img_url, timeout=10, verify=False)
            if ir.status_code == 200 and len(ir.content) >= MIN_IMG_SIZE:
                tmp = f"temp_{i}.jpg"
                with open(tmp, "wb") as f: f.write(ir.content)
                
                prompt_img = """
                【任务】：对企业网站图片进行安全风控审计。
                【判定规则】：如果在图片中发现了“地缘政治实体名称”、“政治口号”、“博彩广告”等与正常商业逻辑完全不符的内容，必须判定为【违规】。
                【回复格式】：正常回复：【安全】，异常回复：【违规】+说明违规内容。
                """
                ok, ai_res = utils_ai.analyze_content(prompt_img, tmp)
                if os.path.exists(tmp): os.remove(tmp)
                
                if ok and "【安全】" not in ai_res:
                    img_risk_count += 1
                    risks.append(f"[图片异常] {img_url} -> {ai_res}")
        except: pass

    print(f"\n       ✅ 完成，发现风险项: {img_risk_count}")
    return risks

def main():
    print("\n==================================================")
    if not verify_ai_health():
        print("\n>>> ⚠️ AI 模块异常，无法执行审计！")
        return

    print(f"\n🚀 开始深度扫描 (系统浏览器内核版)...")
    email_lines = []
    for url in config.SITES:
        current_risks = check_site(url)
        if current_risks:
            email_lines.append(f"❌ {url}")
            for r in current_risks: email_lines.append(f"   └─ {r}")
        print("-" * 30)

    if email_lines:
        body = "<h3>🚨 网站安全告警</h3><pre>{}</pre>".format("\n".join(email_lines))
        # 使用你配置好的 163 企业邮箱发送
        utils_email.send_email("【严重告警】网站内容安全异常", body)
    else:
        print("✅ 全量扫描完成，一切正常。")

if __name__ == "__main__":
    main()