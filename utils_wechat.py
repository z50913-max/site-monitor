import requests
import json
import config
import sys

def send_wecom(markdown_content):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {"content": markdown_content}
    }
    try:
        resp = requests.post(config.WECOM_WEBHOOK, json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        # 检查微信特有的错误码
        res_json = resp.json()
        if res_json.get('errcode') == 0:
            return True, "发送成功"
        else:
            return False, f"微信接口报错: {res_json}"
    except Exception as e:
        return False, f"网络请求异常: {str(e)}"

# === 独立测试入口 ===
if __name__ == "__main__":
    print("--------------------------------------------------")
    print(">>> [1/3] 开始测试：企业微信 (WeChat)")
    print(f"目标地址: {config.WECOM_WEBHOOK}")
    print("正在发送请求...")

    success, msg = send_wecom("### 测试信号\n这是来自 Ubuntu 监控脚本的连通性测试。")

    if success:
        print("\n【测试正常】")
    else:
        print("\n【测试失败】")
        print(f"原因: {msg}")
    print("--------------------------------------------------")