#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从众心理分析 - 点赞互动分析模块
分析社会认同信号和意见领袖识别
"""

import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
sys.path.append('..')

from config.db_config import get_db_conn

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class LikeInteractionAnalyzer:
    def __init__(self):
        self.like_thresholds = {
            'low': 0,           # 低点赞：0
            'medium': 5,        # 中等点赞：5-19
            'high': 20,         # 高点赞：20-99
            'very_high': 100,   # 很高点赞：100-499
            'viral': 500        # 病毒级：500+
        }
        
        self.follow_speed_thresholds = {
            'immediate': 5,      # 立即跟随：5分钟内
            'quick': 30,         # 快速跟随：30分钟内
            'medium': 120,       # 中等跟随：2小时内
            'slow': 1440,        # 缓慢跟随：24小时内
            'delayed': 10080     # 延迟跟随：1周内
        }
    
    def load_data(self, conn, use_cleaned_data=False, cleaned_data_path=None):
        """加载数据"""
        print("=== 加载数据 ===")
        
        if use_cleaned_data and cleaned_data_path:
            # 从清洗数据加载
            df = self.load_from_cleaned_data(cleaned_data_path)
        else:
            # 从数据库加载
            df = self.load_from_database(conn)
        
        if df is None or df.empty:
            print("❌ 没有找到有效数据")
            return None
        
        print(f"✅ 成功加载数据: {len(df)} 条记录")
        return df
    
    def load_from_cleaned_data(self, cleaned_data_path):
        """从清洗数据文件加载"""
        try:
            if not os.path.exists(cleaned_data_path):
                print(f"❌ 清洗数据文件不存在: {cleaned_data_path}")
                return None
            
            with open(cleaned_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            print(f"✅ 成功加载清洗数据: {len(df)} 条记录")
            
            # 检查必要字段
            required_fields = ['comment_id', 'parent_comment_id', 'create_time', 'like_count']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                print(f"❌ 清洗数据缺少必要字段: {missing_fields}")
                return None
            
            # 数据类型转换
            df['like_count'] = pd.to_numeric(df['like_count'], errors='coerce').fillna(0)
            df['create_time'] = pd.to_numeric(df['create_time'], errors='coerce')
            
            # 过滤无效数据
            df = df[df['create_time'].notna()]
            
            return df
            
        except Exception as e:
            print(f"❌ 加载清洗数据失败: {e}")
            return None
    
    def load_from_database(self, conn):
        """从数据库加载数据"""
        sql = """
        SELECT 
            comment_id, aweme_id, parent_comment_id, content, create_time,
            like_count, sub_comment_count, user_id, nickname
        FROM douyin_aweme_comment
        WHERE content IS NOT NULL
        ORDER BY create_time
        """
        
        df = pd.read_sql_query(sql, conn)
        return df
    
    def analyze_like_distribution(self, df):
        """分析点赞数分布"""
        print("\n=== 点赞数分布分析 ===")
        
        # 基础统计
        like_stats = {
            'total_comments': len(df),
            'mean_likes': df['like_count'].mean(),
            'median_likes': df['like_count'].median(),
            'max_likes': df['like_count'].max(),
            'std_likes': df['like_count'].std(),
            'zero_likes': len(df[df['like_count'] == 0]),
            'high_likes': len(df[df['like_count'] >= 20])
        }
        
        print(f"总评论数: {like_stats['total_comments']:,}")
        print(f"平均点赞数: {like_stats['mean_likes']:.2f}")
        print(f"中位数点赞数: {like_stats['median_likes']:.2f}")
        print(f"最高点赞数: {like_stats['max_likes']}")
        print(f"标准差: {like_stats['std_likes']:.2f}")
        print(f"零点赞评论: {like_stats['zero_likes']:,} ({like_stats['zero_likes']/like_stats['total_comments']*100:.1f}%)")
        print(f"高点赞评论(≥20): {like_stats['high_likes']:,} ({like_stats['high_likes']/like_stats['total_comments']*100:.1f}%)")
        
        # 点赞数分布区间统计
        like_ranges = {
            '0点赞': len(df[df['like_count'] == 0]),
            '1-4点赞': len(df[(df['like_count'] >= 1) & (df['like_count'] < 5)]),
            '5-19点赞': len(df[(df['like_count'] >= 5) & (df['like_count'] < 20)]),
            '20-99点赞': len(df[(df['like_count'] >= 20) & (df['like_count'] < 100)]),
            '100-499点赞': len(df[(df['like_count'] >= 100) & (df['like_count'] < 500)]),
            '500+点赞': len(df[df['like_count'] >= 500])
        }
        
        print("\n点赞数分布:")
        for range_name, count in like_ranges.items():
            percentage = (count / like_stats['total_comments']) * 100
            print(f"  {range_name}: {count:,} 条 ({percentage:.1f}%)")
        
        return like_stats, like_ranges
    
    def analyze_parent_child_like_correlation(self, df):
        """分析主评论与子评论点赞数相关性"""
        print("\n=== 主评论与子评论点赞数相关性分析 ===")
        
        # 分离主评论和子评论
        parent_comments = df[df['parent_comment_id'].isna() | (df['parent_comment_id'] == '0')].copy()
        child_comments = df[df['parent_comment_id'].notna() & (df['parent_comment_id'] != '0')].copy()
        
        print(f"主评论数: {len(parent_comments):,}")
        print(f"子评论数: {len(child_comments):,}")
        
        # 主评论点赞统计
        parent_like_stats = {
            'mean': parent_comments['like_count'].mean(),
            'median': parent_comments['like_count'].median(),
            'max': parent_comments['like_count'].max(),
            'high_like_count': len(parent_comments[parent_comments['like_count'] >= 20])
        }
        
        print(f"\n主评论点赞统计:")
        print(f"  平均点赞数: {parent_like_stats['mean']:.2f}")
        print(f"  中位数点赞数: {parent_like_stats['median']:.2f}")
        print(f"  最高点赞数: {parent_like_stats['max']}")
        print(f"  高点赞主评论(≥20): {parent_like_stats['high_like_count']:,}")
        
        # 子评论点赞统计
        child_like_stats = {
            'mean': child_comments['like_count'].mean(),
            'median': child_comments['like_count'].median(),
            'max': child_comments['like_count'].max(),
            'high_like_count': len(child_comments[child_comments['like_count'] >= 20])
        }
        
        print(f"\n子评论点赞统计:")
        print(f"  平均点赞数: {child_like_stats['mean']:.2f}")
        print(f"  中位数点赞数: {child_like_stats['median']:.2f}")
        print(f"  最高点赞数: {child_like_stats['max']}")
        print(f"  高点赞子评论(≥20): {child_like_stats['high_like_count']:,}")
        
        return parent_comments, child_comments, parent_like_stats, child_like_stats
    
    def identify_opinion_leaders(self, df, like_threshold=20, follow_speed_threshold=30):
        """识别意见领袖"""
        print(f"\n=== 意见领袖识别 (点赞≥{like_threshold}, 跟随速度≤{follow_speed_threshold}分钟) ===")
        
        # 分离主评论和子评论
        parent_comments = df[df['parent_comment_id'].isna() | (df['parent_comment_id'] == '0')].copy()
        child_comments = df[df['parent_comment_id'].notna() & (df['parent_comment_id'] != '0')].copy()
        
        # 计算时间差
        if len(child_comments) > 0:
            child_comments = self.calculate_follow_speed(child_comments, parent_comments)
        
        # 识别高点赞主评论
        high_like_parents = parent_comments[parent_comments['like_count'] >= like_threshold].copy()
        
        opinion_leaders = []
        
        for _, parent in high_like_parents.iterrows():
            # 找到该主评论的所有子评论
            child_comments_for_parent = child_comments[
                child_comments['parent_comment_id'] == parent['comment_id']
            ]
            
            if len(child_comments_for_parent) == 0:
                continue
            
            # 计算快速跟随的子评论数量
            quick_follows = child_comments_for_parent[
                child_comments_for_parent['follow_speed_minutes'] <= follow_speed_threshold
            ]
            
            # 计算跟随率
            follow_rate = len(quick_follows) / len(child_comments_for_parent) * 100
            
            # 计算平均跟随速度
            avg_follow_speed = child_comments_for_parent['follow_speed_minutes'].mean()
            
            opinion_leader = {
                'comment_id': parent['comment_id'],
                'content': parent['content'][:50] + '...' if len(parent['content']) > 50 else parent['content'],
                'like_count': parent['like_count'],
                'total_follows': len(child_comments_for_parent),
                'quick_follows': len(quick_follows),
                'follow_rate': follow_rate,
                'avg_follow_speed': avg_follow_speed,
                'influence_score': parent['like_count'] * follow_rate / 100
            }
            
            opinion_leaders.append(opinion_leader)
        
        # 按影响力分数排序
        opinion_leaders.sort(key=lambda x: x['influence_score'], reverse=True)
        
        print(f"识别到 {len(opinion_leaders)} 个潜在意见领袖")
        
        if opinion_leaders:
            print("\n影响力排名前10的意见领袖:")
            for i, leader in enumerate(opinion_leaders[:10], 1):
                print(f"  {i}. 点赞:{leader['like_count']}, 跟随:{leader['total_follows']}条, "
                      f"快速跟随:{leader['quick_follows']}条, 跟随率:{leader['follow_rate']:.1f}%, "
                      f"平均速度:{leader['avg_follow_speed']:.1f}分钟, 影响力:{leader['influence_score']:.1f}")
                print(f"     内容: {leader['content']}")
        
        return opinion_leaders
    
    def calculate_follow_speed(self, child_comments, parent_comments):
        """计算跟随速度"""
        # 创建父评论时间映射
        parent_time_map = parent_comments.set_index('comment_id')['create_time'].to_dict()
        
        def get_follow_speed(row):
            parent_time = parent_time_map.get(row['parent_comment_id'])
            if parent_time:
                time_diff_seconds = row['create_time'] - parent_time
                return time_diff_seconds / 60  # 转换为分钟
            return None
        
        child_comments['follow_speed_minutes'] = child_comments.apply(get_follow_speed, axis=1)
        return child_comments
    
    def analyze_social_approval_signals(self, df):
        """分析社会认同信号"""
        print("\n=== 社会认同信号分析 ===")
        
        # 分离主评论和子评论
        parent_comments = df[df['parent_comment_id'].isna() | (df['parent_comment_id'] == '0')].copy()
        child_comments = df[df['parent_comment_id'].notna() & (df['parent_comment_id'] != '0')].copy()
        
        # 计算时间差
        if len(child_comments) > 0:
            child_comments = self.calculate_follow_speed(child_comments, parent_comments)
        
        # 分析不同点赞水平的主评论的跟随情况
        like_levels = [
            (0, '零点赞'),
            (1, '低点赞(1-4)'),
            (5, '中等点赞(5-19)'),
            (20, '高点赞(20-99)'),
            (100, '很高点赞(100-499)'),
            (500, '病毒级(500+)')
        ]
        
        approval_signals = []
        
        for min_likes, level_name in like_levels:
            if min_likes == 0:
                level_parents = parent_comments[parent_comments['like_count'] == 0]
            else:
                next_level = like_levels[like_levels.index((min_likes, level_name)) + 1][0] if like_levels.index((min_likes, level_name)) + 1 < len(like_levels) else float('inf')
                level_parents = parent_comments[
                    (parent_comments['like_count'] >= min_likes) & 
                    (parent_comments['like_count'] < next_level)
                ]
            
            if len(level_parents) == 0:
                continue
            
            # 统计该级别主评论的跟随情况
            total_follows = 0
            quick_follows = 0
            total_follow_speed = 0
            follow_count = 0
            
            for _, parent in level_parents.iterrows():
                child_comments_for_parent = child_comments[
                    child_comments['parent_comment_id'] == parent['comment_id']
                ]
                
                if len(child_comments_for_parent) > 0:
                    total_follows += len(child_comments_for_parent)
                    quick_follows += len(child_comments_for_parent[
                        child_comments_for_parent['follow_speed_minutes'] <= 30
                    ])
                    total_follow_speed += child_comments_for_parent['follow_speed_minutes'].sum()
                    follow_count += 1
            
            avg_follows = total_follows / len(level_parents) if len(level_parents) > 0 else 0
            quick_follow_rate = (quick_follows / total_follows * 100) if total_follows > 0 else 0
            avg_follow_speed = total_follow_speed / total_follows if total_follows > 0 else 0
            
            signal = {
                'level': level_name,
                'parent_count': len(level_parents),
                'avg_follows': avg_follows,
                'quick_follow_rate': quick_follow_rate,
                'avg_follow_speed': avg_follow_speed,
                'total_follows': total_follows
            }
            
            approval_signals.append(signal)
            
            print(f"\n{level_name}主评论 ({len(level_parents)} 条):")
            print(f"  平均跟随数: {avg_follows:.2f}")
            print(f"  快速跟随率: {quick_follow_rate:.1f}%")
            print(f"  平均跟随速度: {avg_follow_speed:.1f} 分钟")
        
        return approval_signals
    
    def create_visualizations(self, df, like_stats, like_ranges, opinion_leaders, approval_signals, output_dir='../data/visualizations'):
        """创建可视化图表"""
        print(f"\n=== 创建可视化图表 ===")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置图表样式
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('点赞互动分析 - 社会认同信号', fontsize=16, fontweight='bold')
        
        # 1. 点赞数分布直方图
        ax1 = axes[0, 0]
        like_counts = df['like_count'].values
        # 过滤极端值以便更好地显示分布
        filtered_likes = like_counts[like_counts <= 100]
        ax1.hist(filtered_likes, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xlabel('点赞数')
        ax1.set_ylabel('评论数量')
        ax1.set_title('点赞数分布 (≤100)')
        ax1.grid(True, alpha=0.3)
        
        # 添加统计线
        mean_likes = like_stats['mean_likes']
        median_likes = like_stats['median_likes']
        ax1.axvline(mean_likes, color='red', linestyle='--', label=f'平均值: {mean_likes:.1f}')
        ax1.axvline(median_likes, color='orange', linestyle='--', label=f'中位数: {median_likes:.1f}')
        ax1.legend()
        
        # 2. 点赞数区间分布饼图
        ax2 = axes[0, 1]
        ranges = list(like_ranges.keys())
        counts = list(like_ranges.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(ranges)))
        
        wedges, texts, autotexts = ax2.pie(counts, labels=ranges, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        ax2.set_title('点赞数区间分布')
        
        # 3. 意见领袖影响力分析
        ax3 = axes[1, 0]
        if opinion_leaders:
            # 显示前10个意见领袖的影响力分数
            top_leaders = opinion_leaders[:10]
            leader_names = [f"L{i+1}" for i in range(len(top_leaders))]
            influence_scores = [leader['influence_score'] for leader in top_leaders]
            
            bars = ax3.bar(leader_names, influence_scores, alpha=0.7, color='lightcoral')
            ax3.set_xlabel('意见领袖')
            ax3.set_ylabel('影响力分数')
            ax3.set_title('意见领袖影响力排名')
            ax3.grid(True, alpha=0.3)
            
            # 添加数值标签
            for bar, score in zip(bars, influence_scores):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{score:.1f}', ha='center', va='bottom')
        else:
            ax3.text(0.5, 0.5, '无意见领袖数据', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('意见领袖影响力排名')
        
        # 4. 社会认同信号分析
        ax4 = axes[1, 1]
        if approval_signals:
            levels = [signal['level'] for signal in approval_signals]
            quick_rates = [signal['quick_follow_rate'] for signal in approval_signals]
            
            bars = ax4.bar(levels, quick_rates, alpha=0.7, color='lightgreen')
            ax4.set_xlabel('点赞水平')
            ax4.set_ylabel('快速跟随率 (%)')
            ax4.set_title('不同点赞水平的快速跟随率')
            ax4.grid(True, alpha=0.3)
            
            # 旋转x轴标签
            ax4.tick_params(axis='x', rotation=45)
            
            # 添加数值标签
            for bar, rate in zip(bars, quick_rates):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{rate:.1f}%', ha='center', va='bottom')
        else:
            ax4.text(0.5, 0.5, '无社会认同信号数据', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('社会认同信号分析')
        
        plt.tight_layout()
        
        # 保存图表
        output_file = os.path.join(output_dir, 'like_interaction_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 可视化图表已保存到: {output_file}")
        
        # 显示图表
        plt.show()
        
        return output_file
    
    def generate_report(self, df, like_stats, like_ranges, opinion_leaders, approval_signals, output_dir='../data/reports'):
        """生成分析报告"""
        print(f"\n=== 生成分析报告 ===")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 转换numpy类型为Python原生类型
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            else:
                return obj
        
        # 生成报告内容
        report = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_summary': {
                'total_comments': int(len(df)),
                'parent_comments': int(len(df[df['parent_comment_id'].isna() | (df['parent_comment_id'] == '0')])),
                'child_comments': int(len(df[df['parent_comment_id'].notna() & (df['parent_comment_id'] != '0')]))
            },
            'like_statistics': convert_numpy_types(like_stats),
            'like_ranges': convert_numpy_types(like_ranges),
            'opinion_leaders': convert_numpy_types(opinion_leaders[:10]),  # 只保存前10个
            'approval_signals': convert_numpy_types(approval_signals),
            'key_findings': []
        }
        
        # 添加关键发现
        report['key_findings'].append(f"平均点赞数: {float(like_stats['mean_likes']):.2f}")
        report['key_findings'].append(f"高点赞评论比例: {like_stats['high_likes']/like_stats['total_comments']*100:.1f}%")
        report['key_findings'].append(f"识别意见领袖数量: {len(opinion_leaders)}")
        
        if opinion_leaders:
            top_leader = opinion_leaders[0]
            report['key_findings'].append(f"最具影响力意见领袖: 点赞{top_leader['like_count']}, 跟随率{top_leader['follow_rate']:.1f}%")
        
        # 保存报告
        output_file = os.path.join(output_dir, 'like_interaction_analysis_report.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析报告已保存到: {output_file}")
        
        # 打印报告摘要
        print("\n=== 分析报告摘要 ===")
        print(f"分析时间: {report['analysis_time']}")
        print(f"总评论数: {report['data_summary']['total_comments']:,}")
        print(f"主评论数: {report['data_summary']['parent_comments']:,}")
        print(f"子评论数: {report['data_summary']['child_comments']:,}")
        
        print("\n关键发现:")
        for finding in report['key_findings']:
            print(f"  • {finding}")
        
        return output_file

def main():
    """主函数"""
    print("=== 点赞互动分析 - 社会认同信号 ===")
    
    analyzer = LikeInteractionAnalyzer()
    
    try:
        # 获取数据库连接
        conn = get_db_conn()
        print("✅ 数据库连接成功")
        
        # 数据获取方式选择
        print("\n请选择数据获取方式:")
        print("1. 从清洗数据调取 (推荐)")
        print("2. 直接从数据库获取")
        
        choice = input("请输入选择 (1 或 2，默认1): ").strip()
        
        if choice == "2":
            # 直接从数据库获取
            print("\n直接从数据库获取数据...")
            df = analyzer.load_data(conn)
        else:
            # 从清洗数据调取
            print("\n从清洗数据调取...")
            cleaned_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'douyin_comments_processed.json')
            df = analyzer.load_data(conn, use_cleaned_data=True, cleaned_data_path=cleaned_data_path)
        
        if df is None or df.empty:
            print("❌ 没有找到有效数据")
            return
        
        # 分析点赞数分布
        like_stats, like_ranges = analyzer.analyze_like_distribution(df)
        
        # 分析主评论与子评论点赞数相关性
        parent_comments, child_comments, parent_like_stats, child_like_stats = analyzer.analyze_parent_child_like_correlation(df)
        
        # 识别意见领袖
        opinion_leaders = analyzer.identify_opinion_leaders(df)
        
        # 分析社会认同信号
        approval_signals = analyzer.analyze_social_approval_signals(df)
        
        # 创建可视化
        analyzer.create_visualizations(df, like_stats, like_ranges, opinion_leaders, approval_signals)
        
        # 生成报告
        analyzer.generate_report(df, like_stats, like_ranges, opinion_leaders, approval_signals)
        
        print("\n✅ 点赞互动分析完成!")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    main() 