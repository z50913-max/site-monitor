import os
import sys

def run_test(script_name):
    print(f"\n========== 正在调用 {script_name} ==========")
    # 使用 Python 调用系统命令执行脚本
    ret = os.system(f"python3 {script_name}")
    if ret != 0:
        print(f"⚠️  警告: {script_name} 执行过程中出现了错误代码 {ret}")

if __name__ == "__main__":
    print("开始全链路可用性自检...")
    
    run_test("utils_wechat.py")
    run_test("utils_email.py")
    run_test("utils_ai.py")
    
    print("\n========== 自检结束 ==========")