#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试阿里云API连接
基于官方文档：https://help.aliyun.com/document_detail/177236.html
"""

import os
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException

# 加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv未安装，无法自动加载.env文件")
    print("请运行: pip install python-dotenv")

def test_aliyun_connection():
    """测试阿里云API连接"""
    
    # 从环境变量读取API密钥（官方推荐的环境变量名）
    access_key_id = os.getenv('NLP_AK_ENV')
    access_key_secret = os.getenv('NLP_SK_ENV')
    region_id = os.getenv('NLP_REGION_ENV', 'cn-hangzhou')
    
    # 检查API密钥是否已配置
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
        return
    
    print("🔍 测试阿里云API连接")
    print("="*50)
    print(f"AccessKey ID: {access_key_id[:10]}...")
    print(f"Region: {region_id}")
    print("参考文档: https://help.aliyun.com/document_detail/177236.html")
    
    # 创建AcsClient实例
    client = AcsClient(
        access_key_id,
        access_key_secret,
        region_id
    )
    
    # 测试文本
    test_text = "这个产品真的很棒，我非常喜欢！"
    
    # 只测试基础版API（免费版）
    apis_to_test = [
        {
            'name': 'GetSaChGeneral (情感分析-基础版)',
            'action': 'GetSaChGeneral',
            'params': {
                'ServiceCode': 'alinlp',
                'Text': test_text
            }
        }
    ]
    
    for api in apis_to_test:
        print(f"\n🧪 测试API: {api['name']}")
        print("-" * 40)
        
        try:
            # 使用CommonRequest（官方推荐方式）
            request = CommonRequest()
            
            # 设置固定参数（官方文档要求）
            request.set_domain('alinlp.cn-hangzhou.aliyuncs.com')
            request.set_version('2020-06-29')
            request.set_action_name(api['action'])
            
            # 设置API参数
            for key, value in api['params'].items():
                request.add_query_param(key, value)
            
            # 发送请求
            response = client.do_action_with_exception(request)
            result = json.loads(response)
            
            print(f"✅ 成功!")
            print(f"RequestId: {result.get('RequestId', 'N/A')}")
            
            # 解析情感分析结果
            if 'Data' in result:
                data = json.loads(result['Data'])
                if 'result' in data:
                    sentiment_result = data['result']
                    print(f"情感倾向: {sentiment_result.get('sentiment', 'N/A')}")
                    print(f"正面概率: {sentiment_result.get('positive_prob', 'N/A')}")
                    print(f"负面概率: {sentiment_result.get('negative_prob', 'N/A')}")
            
        except ServerException as e:
            print(f"❌ 服务器错误: {e}")
            print(f"错误代码: {e.error_code}")
            print(f"错误信息: {e.message}")
            
            # 根据官方文档提供解决方案
            if e.error_code == 'BasicServiceNotActivated':
                print("\n💡 解决方案：")
                print("请开通基础版服务：https://common-buy.aliyun.com/?commodityCode=nlp_alinlpBasePost_public_cn#/buy")
            elif e.error_code == 'AdvancedServiceNotActivated':
                print("\n💡 解决方案：")
                print("请开通高级版服务：https://common-buy.aliyun.com/?commodityCode=nlp_alinlpAdvancedPost_public_cn#/buy")
            elif e.error_code == 'UserStatusInvalid':
                print("\n💡 解决方案：")
                print("请检查账户是否欠费和有未支付的账单")
            
        except ClientException as e:
            print(f"❌ 客户端错误: {e}")
            print(f"错误代码: {e.error_code}")
            print(f"错误信息: {e.message}")
            
        except Exception as e:
            print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_aliyun_connection() 