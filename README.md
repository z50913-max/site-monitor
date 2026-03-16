# Site Monitor

## 项目简介
这是一个基于 Python 的网站内容安全巡检脚本。  
脚本会访问配置中的站点，抓取页面文本和图片资源，并调用大模型接口进行内容审计；发现异常后通过邮件告警。

## 主要功能
- 动态渲染页面并抓取资源（Playwright + Edge）
- 文本内容安全审计（LLM）
- 图片内容安全审计（LLM 多模态）
- 邮件告警（SMTP）

## 目录说明
- `main_monitor.py`：主程序入口
- `config.py`：监控站点、模型接口、告警配置
- `utils_ai.py`：模型请求封装（支持免密和密钥两种方式）
- `utils_email.py`：SMTP 邮件发送
- `utils_wechat.py`：企业微信机器人发送（当前主流程未默认调用）
- `test_all.py`：连通性测试脚本
- `tishici.txt`：敏感内容审计提示词参考（请保留）
- `monitor_system.log`：运行日志（建议仅本地保留）

## 运行环境
- Python 3.10+
- Windows（默认使用系统 Edge 的 Playwright 渲染）

建议安装依赖：

```bash
pip install requests beautifulsoup4 playwright urllib3
```

## 配置说明
编辑 `config.py`：

1. 站点列表  
- `SITES`：需要巡检的网站 URL（列表格式）

2. 模型接口  
- `LLM_API_URL`：模型服务地址  
- `MODEL_NAME`：模型名称  
- `LLM_API_KEY`：免密服务留空 `""`；需鉴权时填写密钥  
- `LLM_API_KEY_HEADER`：常见为 `Authorization` 或 `X-API-Key`  
- `LLM_API_KEY_PREFIX`：常见为 `Bearer ` 或空字符串 `""`

3. 告警通道  
- `WECOM_WEBHOOK`：企业微信机器人地址（可选）  
- `SMTP_CONFIG`：邮件服务器、账号、密码、收件人

## 启动方式
主程序：

```bash
python main_monitor.py
```

测试脚本：

```bash
python test_all.py
```

## 上传 GitHub 前建议
- 不要提交真实密钥、真实邮箱密码、真实 webhook
- `monitor_system.log` 仅保留空文件或不提交
- 不提交 `__pycache__/` 和 `*.pyc`

## 免责声明
本脚本输出基于模型判断，建议将高风险结果作为告警线索，结合人工复核后再处理。

