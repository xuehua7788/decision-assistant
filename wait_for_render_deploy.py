#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待Render部署完成并验证
"""

import requests
import time

BASE_URL = "https://decision-assistant-backend.onrender.com"

def check_deployment():
    """检查部署状态"""
    print("=" * 70)
    print("等待Render部署完成...")
    print("=" * 70)
    print()
    print("提示: Render自动部署通常需要2-5分钟")
    print("      如果超过5分钟，请检查Render Dashboard")
    print()
    
    max_attempts = 30  # 最多等待5分钟（每10秒检查一次）
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"[{attempt}/{max_attempts}] 检查中...", end=" ")
        
        try:
            # 检查Profile API是否可用
            response = requests.get(
                f"{BASE_URL}/api/profile/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Profile API已就绪！")
                print()
                print("=" * 70)
                print("部署成功！")
                print("=" * 70)
                print()
                print("现在可以测试用户画像功能：")
                print("  python analyze_user.py bbb")
                print()
                return True
            elif response.status_code == 404:
                print("❌ 仍然是旧版本（404）")
            else:
                print(f"⚠️ 状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏱️ 超时（可能正在重启）")
        except requests.exceptions.ConnectionError:
            print("🔄 连接失败（正在部署）")
        except Exception as e:
            print(f"⚠️ {e}")
        
        if attempt < max_attempts:
            time.sleep(10)  # 等待10秒
    
    print()
    print("=" * 70)
    print("⚠️ 超时：部署时间超过预期")
    print("=" * 70)
    print()
    print("请检查:")
    print("1. Render Dashboard: https://dashboard.render.com/")
    print("2. 查看部署日志")
    print("3. 确认自动部署已启用")
    print()
    return False

if __name__ == "__main__":
    print()
    success = check_deployment()
    
    if not success:
        print("如果Render部署成功但此脚本超时，可以手动测试：")
        print("  python diagnose_render.py")
        print()






