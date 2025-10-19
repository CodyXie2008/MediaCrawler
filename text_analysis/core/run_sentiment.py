#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一情感分析脚本
支持本地词典和阿里云API两种分析方式
"""

import os
import sys
import argparse

# 加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv未安装，无法自动加载.env文件")
    print("请运行: pip install python-dotenv")

def setup_aliyun_env():
    """设置阿里云API环境变量"""
    # 检查环境变量是否已设置
    access_key_id = os.getenv('NLP_AK_ENV')
    access_key_secret = os.getenv('NLP_SK_ENV')
    region_id = os.getenv('NLP_REGION_ENV', 'cn-hangzhou')
    
    if not access_key_id or not access_key_secret:
        print("❌ 阿里云API密钥未配置")
        print("请设置以下环境变量：")
        print("  - NLP_AK_ENV: 阿里云AccessKey ID")
        print("  - NLP_SK_ENV: 阿里云AccessKey Secret")
        print("  - NLP_REGION_ENV: 阿里云区域ID (可选，默认为cn-hangzhou)")
        print("\n或者创建 .env 文件并添加：")
        print("  NLP_AK_ENV=your_access_key_id")
        print("  NLP_SK_ENV=your_access_key_secret")
        print("  NLP_REGION_ENV=cn-hangzhou")
        return False
    
    print("✅ 阿里云API环境变量已设置")
    print(f"AccessKey ID: {access_key_id[:10]}...")
    print(f"Region: {region_id}")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="情感分析工具")
    parser.add_argument('--type', choices=['local', 'aliyun'], 
                       default='local', help='分析器类型：local(本地词典) 或 aliyun(阿里云API)')
    parser.add_argument('--auto', action='store_true', 
                       help='自动模式，不显示选择界面')
    
    args = parser.parse_args()
    
    # 根据参数设置环境
    if args.type == 'aliyun':
        print("🚀 阿里云API情感分析")
        print("="*30)
        if not setup_aliyun_env():
            print("❌ 无法启动阿里云API分析，请先配置API密钥")
            return
        print("🔧 正在启动阿里云API情感分析...")
    else:
        print("🚀 本地词典情感分析")
        print("="*30)
        print("✅ 使用本地词典分析（无需网络连接）")
        print("🔧 正在启动本地词典情感分析...")
    
    # 直接导入并运行主程序
    try:
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        sys.path.insert(0, os.path.join(project_root, 'core'))
        
        from sentiment_analysis_simple import main as sentiment_main
        
        # 如果是自动模式，设置环境变量让主程序知道选择的分析器类型
        if args.auto:
            if args.type == 'aliyun':
                os.environ['SENTIMENT_ANALYZER_TYPE'] = 'aliyun'
            else:
                os.environ['SENTIMENT_ANALYZER_TYPE'] = 'local'
        
        sentiment_main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 