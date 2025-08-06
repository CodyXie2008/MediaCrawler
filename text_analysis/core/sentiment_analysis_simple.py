#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版情感分析模块
只支持本地词典和阿里云NLP API
"""

import sys
import os
import re
import json
import time
import requests
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Union
import logging

# 添加项目根目录到Python路径
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config.db_config import get_db_conn

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DictionaryAnalyzer:
    """本地词典情感分析器"""
    
    def __init__(self):
        self.sentiment_dict = self._load_sentiment_dict()
        self.negation_words = {'不', '没', '无', '非', '未', '别', '莫', '勿', '毋', '弗', '否', '反'}
        self.intensifier_words = {
            '非常': 2.0, '特别': 2.0, '极其': 2.0, '十分': 2.0, '很': 1.5, '挺': 1.3,
            '比较': 1.2, '有点': 0.8, '稍微': 0.7, '略微': 0.7, '太': 1.8, '真': 1.5,
            '确实': 1.3, '真的': 1.5, '绝对': 2.0, '完全': 2.0,
        }
    
    def _load_sentiment_dict(self) -> Dict[str, float]:
        """加载情感词典"""
        return {
            # 正向情感词
            '好': 1.0, '棒': 1.0, '赞': 1.0, '优秀': 1.0, '完美': 1.0, '精彩': 1.0,
            '喜欢': 1.0, '爱': 1.0, '支持': 1.0, '推荐': 1.0, '满意': 1.0, '开心': 1.0,
            '高兴': 1.0, '快乐': 1.0, '兴奋': 1.0, '激动': 1.0, '感动': 1.0, '温暖': 1.0,
            '美好': 1.0, '漂亮': 1.0, '帅气': 1.0, '可爱': 1.0, '有趣': 1.0, '搞笑': 1.0,
            '厉害': 1.0, '强大': 1.0, '专业': 1.0, '高质量': 1.0, '超赞': 1.5, '太棒了': 1.5,
            '666': 1.0, '牛': 1.0, '神': 1.0, '绝了': 1.5, '无敌': 1.5, '爆赞': 1.5,
            '加油': 0.8, '好样': 0.8, '棒棒': 1.0, '棒棒哒': 1.2, '棒极了': 1.3,
            '太棒': 1.2, '很棒': 1.1, '非常好': 1.2, '特别好': 1.2, '超级棒': 1.4,
            '太赞': 1.2, '很赞': 1.1, '超赞': 1.3, '赞赞': 1.0, '赞赞赞': 1.2,
            '喜欢': 1.0, '很喜欢': 1.2, '超喜欢': 1.3, '爱了': 1.1, '爱了爱了': 1.3,
            
            # 负向情感词
            '差': -1.0, '烂': -1.0, '垃圾': -1.0, '糟糕': -1.0, '恶心': -1.0, '讨厌': -1.0,
            '恨': -1.0, '烦': -1.0, '生气': -1.0, '愤怒': -1.0, '失望': -1.0, '伤心': -1.0,
            '难过': -1.0, '痛苦': -1.0, '绝望': -1.0, '崩溃': -1.0, '无语': -1.0, '坑': -1.0,
            '骗': -1.0, '假': -1.0, '水': -1.0, '无聊': -1.0, '没意思': -1.0, '浪费时间': -1.0,
            '太差了': -1.5, '太烂了': -1.5, '太恶心了': -1.5, '太坑了': -1.5, '太假了': -1.5,
            '太无聊了': -1.5, '太失望了': -1.5, '太伤心了': -1.5, '太痛苦了': -1.5,
            '很差': -1.1, '非常差': -1.3, '特别差': -1.3, '超级差': -1.4,
            '太烂': -1.2, '很烂': -1.1, '超烂': -1.3, '烂透了': -1.4,
            '讨厌': -1.0, '很讨厌': -1.2, '超讨厌': -1.3, '太讨厌': -1.2,
            '失望': -1.0, '很失望': -1.2, '太失望': -1.3, '非常失望': -1.4,
            
            # 中性情感词
            '一般': 0.0, '还行': 0.0, '凑合': 0.0, '普通': 0.0, '正常': 0.0, '标准': 0.0,
            '可以': 0.0, '不错': 0.0, '还好': 0.0, '马马虎虎': 0.0, '过得去': 0.0,
            '还行': 0.0, '凑合': 0.0, '一般般': 0.0, '马马虎虎': 0.0, '过得去': 0.0,
        }
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """分析文本情感"""
        if not text or not text.strip():
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # 文本预处理
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        words = text.split()
        
        if not words:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        total_score = 0.0
        word_count = 0
        
        for i, word in enumerate(words):
            word_score = 0.0
            
            # 检查情感词典
            if word in self.sentiment_dict:
                word_score = self.sentiment_dict[word]
            
            # 检查程度副词
            if i > 0 and words[i-1] in self.intensifier_words:
                word_score *= self.intensifier_words[words[i-1]]
            
            # 检查否定词
            if i > 0 and words[i-1] in self.negation_words:
                word_score *= -1
            
            total_score += word_score
            word_count += 1
        
        # 计算平均分数
        if word_count > 0:
            score = total_score / word_count
        else:
            score = 0.0
        
        # 确定情感极性
        if score >= 0.3:
            sentiment = 'positive'
        elif score <= -0.3:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # 计算置信度
        confidence = min(abs(score) * 2, 0.9) if abs(score) > 0 else 0.3
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'method': 'dictionary'
        }

class AliyunAnalyzer:
    """阿里云NLP情感分析器"""
    
    def __init__(self):
        self.access_key_id = os.getenv('NLP_AK_ENV')
        self.access_key_secret = os.getenv('NLP_SK_ENV')
        self.region_id = os.getenv('NLP_REGION_ENV', 'cn-hangzhou')
        self.endpoint = f"https://nlp.{self.region_id}.aliyuncs.com"
        
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError("阿里云AccessKey未配置，请设置环境变量NLP_AK_ENV和NLP_SK_ENV")
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """分析文本情感"""
        try:
            # 优先使用SDK
            return self._analyze_with_sdk(text)
        except Exception as e:
            logger.warning(f"SDK分析失败，尝试HTTP请求: {e}")
            try:
                return self._analyze_with_http(text)
            except Exception as e2:
                logger.error(f"HTTP请求也失败: {e2}")
                # 返回默认结果
                return {
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'confidence': 0.0,
                    'error': f"API连接失败: {e2}",
                    'method': 'aliyun'
                }
    
    def _analyze_with_sdk(self, text: str) -> Dict[str, Union[str, float]]:
        """使用SDK分析（基于官方文档）"""
        try:
            import json
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest
            from aliyunsdkcore.acs_exception.exceptions import ClientException
            from aliyunsdkcore.acs_exception.exceptions import ServerException
            
            # 创建AcsClient实例
            client = AcsClient(
                self.access_key_id,
                self.access_key_secret,
                self.region_id
            )
            
            # 使用CommonRequest（官方推荐方式）
            request = CommonRequest()
            
            # 设置固定参数（官方文档要求）
            request.set_domain('alinlp.cn-hangzhou.aliyuncs.com')
            request.set_version('2020-06-29')
            request.set_action_name('GetSaChGeneral')
            
            # 设置API参数
            request.add_query_param('ServiceCode', 'alinlp')
            request.add_query_param('Text', text)
            
            # 发送请求
            response = client.do_action_with_exception(request)
            result = json.loads(response)
            
            return self._parse_response(result)
            
        except ImportError:
            raise Exception("阿里云SDK未安装")
        except Exception as e:
            raise e
    
    def _analyze_with_http(self, text: str) -> Dict[str, Union[str, float]]:
        """使用HTTP请求分析"""
        params = {
            'Action': 'SentimentAnalysis',
            'Version': '2018-04-08',
            'Format': 'JSON',
            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'SignatureNonce': str(int(time.time() * 1000)),
            'AccessKeyId': self.access_key_id,
            'Text': text,
        }
        
        # 生成签名
        signature = self._generate_signature('POST', '/', params)
        params['Signature'] = signature
        
        try:
            response = requests.post(self.endpoint, data=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            return self._parse_response(result)
        except Exception as e:
            raise e
    
    def _generate_signature(self, method: str, path: str, params: Dict) -> str:
        """生成签名"""
        canonicalized_query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        string_to_sign = f"{method}\n{path}\n{canonicalized_query_string}\n"
        
        signature = hmac.new(
            self.access_key_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _parse_response(self, result: Dict) -> Dict[str, Union[str, float]]:
        """解析响应"""
        try:
            # 解析Data字段（可能是JSON字符串）
            data_str = result.get('Data', '{}')
            if isinstance(data_str, str):
                import json
                data = json.loads(data_str)
            else:
                data = data_str
            
            # 获取结果
            result_data = data.get('result', {})
            sentiment_zh = result_data.get('sentiment', '')
            positive_prob = float(result_data.get('positive_prob', 0))
            negative_prob = float(result_data.get('negative_prob', 0))
            neutral_prob = float(result_data.get('neutral_prob', 0))
            
            # 映射情感
            sentiment_map = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                '正向': 'positive',
                '负向': 'negative',
                '中性': 'neutral',
                '正面': 'positive',
                '负面': 'negative',
            }
            
            sentiment = sentiment_map.get(sentiment_zh.lower(), 'neutral')
            
            # 计算分数和置信度
            if sentiment == 'positive':
                score = positive_prob
                confidence = positive_prob
            elif sentiment == 'negative':
                score = -negative_prob
                confidence = negative_prob
            else:
                score = 0.0
                confidence = neutral_prob
            
            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': confidence,
                'positive_prob': positive_prob,
                'negative_prob': negative_prob,
                'neutral_prob': neutral_prob,
                'method': 'aliyun'
            }
        except Exception as e:
            raise e

class SentimentManager:
    """情感分析管理器"""
    
    def __init__(self, analyzer_type: str = "dictionary"):
        """
        初始化情感分析管理器
        
        Args:
            analyzer_type: 分析器类型 ("dictionary" 或 "aliyun")
        """
        self.analyzer_type = analyzer_type
        
        if analyzer_type == "dictionary":
            self.analyzer = DictionaryAnalyzer()
        elif analyzer_type == "aliyun":
            self.analyzer = AliyunAnalyzer()
        else:
            raise ValueError(f"不支持的分析器类型: {analyzer_type}")
        
        self.stats = {
            'total_analyzed': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'total_confidence': 0.0,
            'total_score': 0.0,
            'errors': 0
        }
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """分析单个文本"""
        try:
            result = self.analyzer.analyze_text(text)
            self._update_stats(result)
            return result
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            self.stats['errors'] += 1
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'error': str(e),
                'method': self.analyzer_type
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Union[str, float]]]:
        """批量分析文本"""
        results = []
        for text in texts:
            result = self.analyze_text(text)
            results.append(result)
        return results
    
    def analyze_from_db(self, conn, limit: int = 100) -> pd.DataFrame:
        """从数据库分析评论"""
        print("=== 从数据库加载评论数据 ===")
        
        sql = """
        SELECT comment_id, content, create_time, like_count
        FROM douyin_aweme_comment
        WHERE content IS NOT NULL AND LENGTH(content) > 5
        ORDER BY create_time DESC
        LIMIT %s
        """
        
        try:
            df = pd.read_sql_query(sql, conn, params=[limit])
            print(f"✅ 成功加载 {len(df)} 条评论")
            
            if df.empty:
                print("⚠️ 没有找到符合条件的评论")
                return df
            
            # 进行情感分析
            print("=== 开始情感分析 ===")
            sentiments = []
            scores = []
            confidences = []
            
            for idx, row in df.iterrows():
                if idx % 50 == 0:
                    print(f"正在分析第 {idx+1}/{len(df)} 条评论...")
                
                result = self.analyze_text(row['content'])
                sentiments.append(result['sentiment'])
                scores.append(result['score'])
                confidences.append(result['confidence'])
            
            # 添加结果到DataFrame
            df['sentiment'] = sentiments
            df['sentiment_score'] = scores
            df['sentiment_confidence'] = confidences
            
            print("✅ 情感分析完成")
            return df
            
        except Exception as e:
            print(f"❌ 数据库分析失败: {e}")
            return pd.DataFrame()
    
    def _update_stats(self, result: Dict[str, Union[str, float]]):
        """更新统计信息"""
        self.stats['total_analyzed'] += 1
        self.stats['total_confidence'] += result.get('confidence', 0.0)
        self.stats['total_score'] += result.get('score', 0.0)
        
        sentiment = result.get('sentiment', 'neutral')
        if sentiment == 'positive':
            self.stats['positive_count'] += 1
        elif sentiment == 'negative':
            self.stats['negative_count'] += 1
        else:
            self.stats['neutral_count'] += 1
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        if stats['total_analyzed'] > 0:
            stats['avg_confidence'] = stats['total_confidence'] / stats['total_analyzed']
            stats['avg_score'] = stats['total_score'] / stats['total_analyzed']
        else:
            stats['avg_confidence'] = 0.0
            stats['avg_score'] = 0.0
        return stats
    
    def save_results(self, df: pd.DataFrame, output_file: str):
        """保存分析结果"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 保存为CSV
        csv_file = output_file.replace('.json', '.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"✅ 结果已保存到: {csv_file}")
        
        # 保存为JSON
        results = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analyzer_type': self.analyzer_type,
            'total_comments': len(df),
            'stats': self.get_stats(),
            'data': df.to_dict('records')
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到: {output_file}")
    
    def generate_report(self, df: pd.DataFrame, output_file: str):
        """生成分析报告"""
        print("=== 生成分析报告 ===")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 统计信息
        stats = self.get_stats()
        sentiment_counts = df['sentiment'].value_counts()
        
        # 生成报告
        report = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analyzer_type': self.analyzer_type,
            'summary': {
                'total_comments': len(df),
                'positive_count': int(sentiment_counts.get('positive', 0)),
                'negative_count': int(sentiment_counts.get('negative', 0)),
                'neutral_count': int(sentiment_counts.get('neutral', 0)),
                'avg_confidence': float(stats['avg_confidence']),
                'avg_score': float(stats['avg_score'])
            },
            'sentiment_distribution': sentiment_counts.to_dict(),
            'top_positive_comments': df[df['sentiment'] == 'positive'].nlargest(5, 'sentiment_score')[['content', 'sentiment_score']].to_dict('records'),
            'top_negative_comments': df[df['sentiment'] == 'negative'].nsmallest(5, 'sentiment_score')[['content', 'sentiment_score']].to_dict('records'),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析报告已保存到: {output_file}")
        
        # 打印报告摘要
        print("\n=== 分析报告摘要 ===")
        print(f"分析时间: {report['analysis_time']}")
        print(f"分析器类型: {report['analyzer_type']}")
        print(f"总评论数: {report['summary']['total_comments']:,}")
        print(f"正向评论: {report['summary']['positive_count']:,} ({report['summary']['positive_count']/report['summary']['total_comments']*100:.1f}%)")
        print(f"负向评论: {report['summary']['negative_count']:,} ({report['summary']['negative_count']/report['summary']['total_comments']*100:.1f}%)")
        print(f"中性评论: {report['summary']['neutral_count']:,} ({report['summary']['neutral_count']/report['summary']['total_comments']*100:.1f}%)")
        print(f"平均置信度: {report['summary']['avg_confidence']:.3f}")
        print(f"平均情感分数: {report['summary']['avg_score']:.3f}")
    
    def create_visualizations(self, df: pd.DataFrame, output_dir: str = None):
        """创建可视化图表"""
        print("=== 创建可视化图表 ===")
        
        # 设置输出目录
        if output_dir is None:
            import sys
            import os
            # 直接使用项目根目录的data文件夹
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            output_dir = os.path.join(project_root, 'data', 'visualizations')
        
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('情感分析结果可视化', fontsize=16, fontweight='bold')
        
        # 1. 情感分布饼图
        ax1 = axes[0, 0]
        sentiment_counts = df['sentiment'].value_counts()
        colors = ['lightgreen', 'lightcoral', 'lightblue']
        wedges, texts, autotexts = ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('情感分布')
        
        # 2. 情感分数分布直方图
        ax2 = axes[0, 1]
        ax2.hist(df['sentiment_score'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.set_xlabel('情感分数')
        ax2.set_ylabel('频次')
        ax2.set_title('情感分数分布')
        ax2.grid(True, alpha=0.3)
        
        # 3. 置信度分布
        ax3 = axes[1, 0]
        ax3.hist(df['sentiment_confidence'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        ax3.set_xlabel('置信度')
        ax3.set_ylabel('频次')
        ax3.set_title('置信度分布')
        ax3.grid(True, alpha=0.3)
        
        # 4. 情感分数vs置信度散点图
        ax4 = axes[1, 1]
        scatter = ax4.scatter(df['sentiment_score'], df['sentiment_confidence'], 
                            c=df['sentiment_score'], cmap='RdYlGn', alpha=0.6)
        ax4.set_xlabel('情感分数')
        ax4.set_ylabel('置信度')
        ax4.set_title('情感分数 vs 置信度')
        ax4.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax4)
        
        plt.tight_layout()
        
        # 保存图表
        output_file = os.path.join(output_dir, 'sentiment_analysis_visualization.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 可视化图表已保存到: {output_file}")
        
        # 显示图表
        plt.show()

def main():
    """主函数"""
    print("=== 简化版情感分析模块 ===")
    
    # 选择分析器类型
    print("\n请选择情感分析器类型:")
    print("1. 本地词典分析")
    print("2. 阿里云NLP API")
    
    choice = input("请输入选择 (1-2，默认1): ").strip()
    
    if choice == "2":
        analyzer_type = "aliyun"
        print("使用阿里云NLP API进行分析")
    else:
        analyzer_type = "dictionary"
        print("使用本地词典进行分析")
    
    # 创建分析管理器
    try:
        manager = SentimentManager(analyzer_type)
        print("✅ 情感分析管理器初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 连接数据库
    try:
        conn = get_db_conn()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    try:
        # 获取分析数量
        try:
            limit = input("请输入要分析的评论数量 (默认100): ").strip()
            limit = int(limit) if limit.isdigit() else 100
        except (EOFError, KeyboardInterrupt):
            limit = 50  # 默认使用50条进行测试
            print(f"使用默认数量: {limit}")
        
        # 分析评论
        print(f"\n开始分析 {limit} 条评论...")
        df = manager.analyze_from_db(conn, limit=limit)
        
        if df.empty:
            print("❌ 没有找到评论数据")
            return
        
        # 保存结果
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from data_paths import PathManager
        paths = PathManager.get_sentiment_analysis_paths()
        manager.save_results(df, paths['results_json'])
        
        # 生成报告
        manager.generate_report(df, paths['report'])
        
        # 创建可视化
        manager.create_visualizations(df)
        
        print("\n✅ 情感分析完成!")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    main() 