import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config
import sys

def send_email(subject, content_html):
    """
    发送邮件 - 修复超时问题版
    """
    try:
        message = MIMEText(content_html, 'html', 'utf-8')
        message['From'] = Header(f"监控中心 <{config.SMTP_CONFIG['user']}>", 'utf-8')
        message['To'] = Header(",".join(config.SMTP_CONFIG['to_addrs']), 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        print(f"1. 正在连接 SMTP 服务器 ({config.SMTP_CONFIG['host']})...", end="", flush=True)
        
        # 【修改点】超时时间增加到 30 秒
        timeout_sec = 30
        
        if config.SMTP_CONFIG['port'] == 465:
            server = smtplib.SMTP_SSL(config.SMTP_CONFIG['host'], config.SMTP_CONFIG['port'], timeout=timeout_sec)
        else:
            server = smtplib.SMTP(config.SMTP_CONFIG['host'], config.SMTP_CONFIG['port'], timeout=timeout_sec)
        
        server.set_debuglevel(0) 
        print(" OK") 

        print(f"2. 正在验证账户...", end="", flush=True)
        server.login(config.SMTP_CONFIG['user'], config.SMTP_CONFIG['password'])
        print(" OK")

        print(f"3. 正在投递邮件...", end="", flush=True)
        server.sendmail(config.SMTP_CONFIG['user'], config.SMTP_CONFIG['to_addrs'], message.as_string())
        server.quit()
        print(" OK")

        return True, "发送成功"
    
    except Exception as e:
        print(" Failed") 
        return False, f"错误: {str(e)}"