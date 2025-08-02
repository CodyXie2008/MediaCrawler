#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从众心理分析 - 时间分析模块
分析从众行为的时间窗口检测
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

class ConformityTimeAnalyzer:
    def __init__(self):
        self.time_windows = {
            'immediate': (0, 5),      # 0-5分钟：立即从众
            'quick': (5, 30),         # 5-30分钟：快速从众
            'medium': (30, 120),      # 30分钟-2小时：中等从众
            'slow': (120, 1440),      # 2小时-24小时：缓慢从众
            'delayed': (1440, 10080), # 1天-1周：延迟从众
            'long_term': (10080, None) # 1周以上：长期从众
        }
        
    def calculate_time_differences(self, conn, aweme_id=None, use_cleaned_data=False, cleaned_data_path=None):
        """计算子评论与父评论的时间差
        
        Args:
            conn: 数据库连接
            aweme_id: 视频ID，None表示分析所有视频
            use_cleaned_data: 是否使用清洗后的数据
            cleaned_data_path: 清洗数据文件路径
        """
        print("=== 计算时间差 ===")
        
        if use_cleaned_data and cleaned_data_path:
            # 从清洗数据调取
            print("从清洗数据调取时间信息...")
            df = self.load_from_cleaned_data(cleaned_data_path)
            if df is None or df.empty:
                print("❌ 清洗数据为空或加载失败，切换到数据库获取")
                return self.calculate_time_differences_from_db(conn, aweme_id)
        else:
            # 直接从数据库获取
            return self.calculate_time_differences_from_db(conn, aweme_id)
        
        return df
    
    def load_from_cleaned_data(self, cleaned_data_path):
        """从清洗数据文件加载数据"""
        try:
            # 检查文件是否存在
            if not os.path.exists(cleaned_data_path):
                print(f"❌ 清洗数据文件不存在: {cleaned_data_path}")
                return None
            
            # 加载JSON数据
            with open(cleaned_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            print(f"✅ 成功加载清洗数据: {len(df)} 条记录")
            
            # 检查必要字段
            required_fields = ['comment_id', 'parent_comment_id', 'create_time']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                print(f"❌ 清洗数据缺少必要字段: {missing_fields}")
                return None
            
            # 过滤有效的子评论（有父评论ID且不为0）
            df_filtered = df[
                (df['parent_comment_id'].notna()) & 
                (df['parent_comment_id'] != '0') & 
                (df['parent_comment_id'] != 0)
            ].copy()
            
            print(f"✅ 有效子评论数据: {len(df_filtered)} 条")
            
            # 计算时间差
            df_filtered = self.calculate_time_differences_from_data(df_filtered)
            
            return df_filtered
            
        except Exception as e:
            print(f"❌ 加载清洗数据失败: {e}")
            return None
    
    def calculate_time_differences_from_db(self, conn, aweme_id=None):
        """直接从数据库计算时间差"""
        # 构建SQL查询
        if aweme_id:
            # 针对特定视频
            sql = """
            SELECT 
                c_child.comment_id,
                c_parent.comment_id AS parent_comment_id,
                c_child.aweme_id,
                c_child.content AS child_content,
                c_parent.content AS parent_content,
                c_child.create_time AS child_time,
                c_parent.create_time AS parent_time,
                TIMESTAMPDIFF(MINUTE, 
                    FROM_UNIXTIME(c_parent.create_time),
                    FROM_UNIXTIME(c_child.create_time)
                ) AS time_diff_minutes,
                TIMESTAMPDIFF(SECOND, 
                    FROM_UNIXTIME(c_parent.create_time),
                    FROM_UNIXTIME(c_child.create_time)
                ) AS time_diff_seconds
            FROM douyin_aweme_comment c_child
            JOIN douyin_aweme_comment c_parent
                ON c_child.parent_comment_id = c_parent.comment_id
            WHERE c_child.aweme_id = %s
                AND c_child.parent_comment_id != '0'
                AND c_child.parent_comment_id IS NOT NULL
            ORDER BY c_parent.create_time, c_child.create_time
            """
            df = pd.read_sql_query(sql, conn, params=[aweme_id])
        else:
            # 所有视频
            sql = """
            SELECT 
                c_child.comment_id,
                c_parent.comment_id AS parent_comment_id,
                c_child.aweme_id,
                c_child.content AS child_content,
                c_parent.content AS parent_content,
                c_child.create_time AS child_time,
                c_parent.create_time AS parent_time,
                TIMESTAMPDIFF(MINUTE, 
                    FROM_UNIXTIME(c_parent.create_time),
                    FROM_UNIXTIME(c_child.create_time)
                ) AS time_diff_minutes,
                TIMESTAMPDIFF(SECOND, 
                    FROM_UNIXTIME(c_parent.create_time),
                    FROM_UNIXTIME(c_child.create_time)
                ) AS time_diff_seconds
            FROM douyin_aweme_comment c_child
            JOIN douyin_aweme_comment c_parent
                ON c_child.parent_comment_id = c_parent.comment_id
            WHERE c_child.parent_comment_id != '0'
                AND c_child.parent_comment_id IS NOT NULL
            ORDER BY c_parent.create_time, c_child.create_time
            """
            df = pd.read_sql_query(sql, conn)
        
        print(f"找到 {len(df)} 条子评论")
        
        # 过滤无效的时间差（负值或异常值）
        df = df[df['time_diff_minutes'] >= 0]
        df = df[df['time_diff_minutes'] <= 10080]  # 过滤超过1周的数据
        
        print(f"有效时间差数据: {len(df)} 条")
        
        return df
    
    def calculate_time_differences_from_data(self, df):
        """从清洗数据计算时间差"""
        print("计算子评论与父评论的时间差...")
        
        # 创建时间映射
        time_map = df.set_index('comment_id')['create_time'].to_dict()
        
        def get_time_diff(row):
            if pd.isna(row['parent_comment_id']) or row['parent_comment_id'] == '0':
                return None
            
            parent_time = time_map.get(row['parent_comment_id'])
            if parent_time:
                return row['create_time'] - parent_time
            return None
        
        df['time_diff_seconds'] = df.apply(get_time_diff, axis=1)
        df['time_diff_minutes'] = df['time_diff_seconds'].apply(lambda x: x/60 if x is not None else None)
        
        # 过滤无效的时间差（负值或异常值）
        df = df[df['time_diff_minutes'] >= 0]
        df = df[df['time_diff_minutes'] <= 10080]  # 过滤超过1周的数据
        
        print(f"有效时间差数据: {len(df)} 条")
        
        return df
    
    def analyze_time_distribution(self, df):
        """分析时间差分布"""
        print("\n=== 时间差分布分析 ===")
        
        time_diffs = df['time_diff_minutes'].dropna()
        
        if len(time_diffs) == 0:
            print("❌ 没有有效的时间差数据")
            return None
        
        # 基础统计
        stats = {
            'count': len(time_diffs),
            'mean': time_diffs.mean(),
            'median': time_diffs.median(),
            'std': time_diffs.std(),
            'min': time_diffs.min(),
            'max': time_diffs.max(),
            'q25': time_diffs.quantile(0.25),
            'q75': time_diffs.quantile(0.75)
        }
        
        print(f"总子评论数: {stats['count']:,} 条")
        print(f"平均回复时间: {stats['mean']:.2f} 分钟")
        print(f"中位数回复时间: {stats['median']:.2f} 分钟")
        print(f"标准差: {stats['std']:.2f} 分钟")
        print(f"最短回复时间: {stats['min']:.2f} 分钟")
        print(f"最长回复时间: {stats['max']:.2f} 分钟")
        print(f"25%分位数: {stats['q25']:.2f} 分钟")
        print(f"75%分位数: {stats['q75']:.2f} 分钟")
        
        # 时间窗口分布
        window_stats = self.calculate_window_distribution(time_diffs)
        
        return stats, window_stats
    
    def calculate_window_distribution(self, time_diffs):
        """计算各时间窗口的分布"""
        print("\n=== 时间窗口分布 ===")
        
        window_counts = {}
        window_percentages = {}
        
        for window_name, (min_time, max_time) in self.time_windows.items():
            if max_time is None:
                # 长期从众：超过1周
                mask = time_diffs >= min_time
            else:
                # 其他窗口
                mask = (time_diffs >= min_time) & (time_diffs < max_time)
            
            count = mask.sum()
            percentage = (count / len(time_diffs)) * 100
            
            window_counts[window_name] = count
            window_percentages[window_name] = percentage
            
            # 显示窗口信息
            if max_time is None:
                time_range = f"{min_time}分钟以上"
            else:
                time_range = f"{min_time}-{max_time}分钟"
            
            print(f"{window_name}: {count:,} 条 ({percentage:.1f}%) - {time_range}")
        
        return {
            'counts': window_counts,
            'percentages': window_percentages
        }
    
    def detect_conformity_windows(self, df, threshold_percentage=10):
        """检测从众行为时间窗口"""
        print(f"\n=== 从众行为时间窗口检测 (阈值: {threshold_percentage}%) ===")
        
        time_diffs = df['time_diff_minutes'].dropna()
        
        if len(time_diffs) == 0:
            print("❌ 没有有效的时间差数据")
            return None
        
        # 按分钟统计评论数量
        minute_counts = time_diffs.value_counts().sort_index()
        
        # 计算累计百分比
        cumulative_percentage = (minute_counts.cumsum() / len(time_diffs)) * 100
        
        # 找到关键时间点
        key_points = {}
        
        # 找到达到10%、25%、50%、75%、90%的时间点
        for target_percentage in [10, 25, 50, 75, 90]:
            try:
                time_point = cumulative_percentage[cumulative_percentage >= target_percentage].index[0]
                key_points[f'{target_percentage}%'] = time_point
                print(f"{target_percentage}%的评论在 {time_point} 分钟内完成")
            except IndexError:
                print(f"{target_percentage}%的评论在数据范围内未达到")
        
        # 检测密集回复时间段
        dense_periods = self.find_dense_periods(minute_counts, threshold_percentage)
        
        return {
            'key_points': key_points,
            'dense_periods': dense_periods,
            'minute_counts': minute_counts,
            'cumulative_percentage': cumulative_percentage
        }
    
    def find_dense_periods(self, minute_counts, threshold_percentage):
        """查找密集回复时间段"""
        print(f"\n=== 密集回复时间段检测 ===")
        
        total_comments = minute_counts.sum()
        threshold_count = (threshold_percentage / 100) * total_comments
        
        # 使用滑动窗口查找密集时间段
        window_size = 5  # 5分钟窗口
        dense_periods = []
        
        for i in range(len(minute_counts) - window_size + 1):
            window_sum = minute_counts.iloc[i:i+window_size].sum()
            if window_sum >= threshold_count:
                start_minute = minute_counts.index[i]
                end_minute = minute_counts.index[i+window_size-1]
                dense_periods.append({
                    'start': start_minute,
                    'end': end_minute,
                    'count': window_sum,
                    'percentage': (window_sum / total_comments) * 100
                })
        
        # 合并相邻的密集时间段
        if dense_periods:
            merged_periods = [dense_periods[0]]
            for period in dense_periods[1:]:
                last_period = merged_periods[-1]
                if period['start'] <= last_period['end'] + 1:
                    # 合并时间段
                    merged_periods[-1]['end'] = period['end']
                    merged_periods[-1]['count'] += period['count']
                    merged_periods[-1]['percentage'] = (merged_periods[-1]['count'] / total_comments) * 100
                else:
                    merged_periods.append(period)
            
            print("检测到的密集回复时间段:")
            for i, period in enumerate(merged_periods, 1):
                print(f"  时间段{i}: {period['start']}-{period['end']}分钟, "
                      f"{period['count']}条评论 ({period['percentage']:.1f}%)")
            
            return merged_periods
        
        print("未检测到明显的密集回复时间段")
        return []
    
    def create_visualizations(self, df, analysis_results, output_dir='../data/visualizations'):
        """创建时间分析可视化图表"""
        print(f"\n=== 创建可视化图表 ===")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置图表样式
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('从众心理时间分析', fontsize=16, fontweight='bold')
        
        time_diffs = df['time_diff_minutes'].dropna()
        
        # 1. 时间差直方图
        ax1 = axes[0, 0]
        ax1.hist(time_diffs, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xlabel('时间差（分钟）')
        ax1.set_ylabel('评论数量')
        ax1.set_title('子评论回复时间分布')
        ax1.grid(True, alpha=0.3)
        
        # 添加统计信息
        mean_time = time_diffs.mean()
        median_time = time_diffs.median()
        ax1.axvline(mean_time, color='red', linestyle='--', label=f'平均值: {mean_time:.1f}分钟')
        ax1.axvline(median_time, color='orange', linestyle='--', label=f'中位数: {median_time:.1f}分钟')
        ax1.legend()
        
        # 2. 累计分布曲线
        ax2 = axes[0, 1]
        # 直接计算累计分布，不依赖analysis_results
        if len(time_diffs) > 0:
            # 按分钟统计评论数量
            minute_counts = time_diffs.value_counts().sort_index()
            # 计算累计百分比
            cumulative_percentage = (minute_counts.cumsum() / len(time_diffs)) * 100
            
            ax2.plot(cumulative_percentage.index, cumulative_percentage.values, linewidth=2, color='green')
            ax2.set_xlabel('时间差（分钟）')
            ax2.set_ylabel('累计百分比（%）')
            ax2.set_title('累计回复时间分布')
            ax2.grid(True, alpha=0.3)
            
            # 标记关键点
            key_points = {}
            for target_percentage in [10, 25, 50, 75, 90]:
                try:
                    time_point = cumulative_percentage[cumulative_percentage >= target_percentage].index[0]
                    key_points[f'{target_percentage}%'] = time_point
                    if time_point in cumulative_percentage.index:
                        percentage = cumulative_percentage[time_point]
                        ax2.scatter(time_point, percentage, color='red', s=50, zorder=5)
                        ax2.annotate(f'{target_percentage}%\n{time_point}分钟', 
                                   (time_point, percentage), 
                                   xytext=(10, 10), textcoords='offset points',
                                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
                except IndexError:
                    continue
        else:
            ax2.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('累计回复时间分布')
        
        # 3. 时间窗口分布饼图
        ax3 = axes[1, 0]
        # 直接计算时间窗口分布，不依赖analysis_results
        window_counts = {}
        for window_name, (min_time, max_time) in self.time_windows.items():
            if max_time is None:
                mask = time_diffs >= min_time
            else:
                mask = (time_diffs >= min_time) & (time_diffs < max_time)
            window_counts[window_name] = mask.sum()
        
        # 只显示有数据的窗口
        non_zero_data = [(name, count) for name, count in window_counts.items() if count > 0]
        if non_zero_data:
            names, counts = zip(*non_zero_data)
            colors = plt.cm.Set3(np.linspace(0, 1, len(names)))
            
            wedges, texts, autotexts = ax3.pie(counts, labels=names, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax3.set_title('时间窗口分布')
        else:
            ax3.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('时间窗口分布')
        
        # 4. 分钟级评论数量分布
        ax4 = axes[1, 1]
        if len(time_diffs) > 0:
            # 直接计算分钟级分布
            minute_counts = time_diffs.value_counts().sort_index()
            # 只显示前100分钟的数据，避免图表过于密集
            display_data = minute_counts.head(100)
            if len(display_data) > 0:
                ax4.bar(display_data.index, display_data.values, alpha=0.7, color='lightcoral')
                ax4.set_xlabel('时间差（分钟）')
                ax4.set_ylabel('评论数量')
                ax4.set_title('分钟级评论数量分布（前100分钟）')
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('分钟级评论数量分布')
        else:
            ax4.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('分钟级评论数量分布')
        
        plt.tight_layout()
        
        # 保存图表
        output_file = os.path.join(output_dir, 'conformity_time_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ 可视化图表已保存到: {output_file}")
        
        # 显示图表
        plt.show()
        
        return output_file
    
    def generate_report(self, df, analysis_results, output_dir='../data/reports'):
        """生成时间分析报告"""
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
            elif hasattr(obj, 'to_dict'):  # pandas Series
                return obj.to_dict()
            elif hasattr(obj, 'tolist'):  # pandas Index
                return obj.tolist()
            else:
                return obj
        
        # 生成报告内容
        report = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_summary': {
                'total_child_comments': int(len(df)),
                'valid_time_diffs': int(len(df['time_diff_minutes'].dropna())),
                'videos_analyzed': int(df['aweme_id'].nunique() if 'aweme_id' in df.columns else 1)
            },
            'time_statistics': convert_numpy_types(analysis_results.get('stats', {})),
            'window_distribution': convert_numpy_types(analysis_results.get('window_stats', {})),
            'conformity_windows': convert_numpy_types(analysis_results.get('conformity_windows', {})),
            'key_findings': []
        }
        
        # 添加关键发现
        if analysis_results and 'stats' in analysis_results:
            stats = analysis_results['stats']
            report['key_findings'].append(f"平均回复时间: {float(stats['mean']):.2f} 分钟")
            report['key_findings'].append(f"中位数回复时间: {float(stats['median']):.2f} 分钟")
            report['key_findings'].append(f"75%的评论在 {float(stats['q75']):.2f} 分钟内完成")
        
        if analysis_results and 'window_stats' in analysis_results:
            window_stats = analysis_results['window_stats']
            # 找到最多的窗口
            max_window = max(window_stats['counts'].items(), key=lambda x: x[1])
            report['key_findings'].append(f"主要从众时间窗口: {max_window[0]} ({int(max_window[1])} 条评论)")
        
        # 保存报告
        output_file = os.path.join(output_dir, 'conformity_time_analysis_report.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析报告已保存到: {output_file}")
        
        # 打印报告摘要
        print("\n=== 分析报告摘要 ===")
        print(f"分析时间: {report['analysis_time']}")
        print(f"总子评论数: {report['data_summary']['total_child_comments']:,}")
        print(f"有效时间差数据: {report['data_summary']['valid_time_diffs']:,}")
        print(f"分析视频数: {report['data_summary']['videos_analyzed']}")
        
        print("\n关键发现:")
        for finding in report['key_findings']:
            print(f"  • {finding}")
        
        return output_file

def main():
    """主函数"""
    print("=== 从众心理时间分析 ===")
    
    analyzer = ConformityTimeAnalyzer()
    
    try:
        # 获取数据库连接
        conn = get_db_conn()
        print("✅ 数据库连接成功")
        
        # 数据获取方式选择
        print("\n请选择数据获取方式:")
        print("1. 从清洗数据调取 (推荐，数据质量更高)")
        print("2. 直接从数据库获取 (原始数据，完整性更好)")
        
        choice = input("请输入选择 (1 或 2，默认1): ").strip()
        
        if choice == "2":
            # 直接从数据库获取
            print("\n直接从数据库获取数据...")
            df = analyzer.calculate_time_differences(conn)
        else:
            # 从清洗数据调取
            print("\n从清洗数据调取...")
            cleaned_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'douyin_comments_processed.json')
            df = analyzer.calculate_time_differences(conn, use_cleaned_data=True, cleaned_data_path=cleaned_data_path)
        
        if df.empty:
            print("❌ 没有找到子评论数据")
            return
        
        # 分析时间分布
        stats, window_stats = analyzer.analyze_time_distribution(df)
        
        # 检测从众时间窗口
        conformity_results = analyzer.detect_conformity_windows(df)
        
        # 整合分析结果
        analysis_results = {
            'stats': stats,
            'window_stats': window_stats,
            'conformity_windows': conformity_results
        }
        
        # 创建可视化
        analyzer.create_visualizations(df, analysis_results)
        
        # 生成报告
        analyzer.generate_report(df, analysis_results)
        
        print("\n✅ 从众心理时间分析完成!")
        
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