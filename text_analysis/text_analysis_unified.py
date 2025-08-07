#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分析统一入口
提供所有分析模块的统一接口，支持情感分析、时间分析、点赞分析、数据清洗
"""

import os
import sys
import argparse
from typing import Optional

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="文本分析统一工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
推荐分析流程:
  1. 首先运行数据清洗
     python text_analysis_unified.py cleaning --video-id 123456
  
  2. 时间分析（使用清洗数据）
     python text_analysis_unified.py time --use-cleaned-data --video-id 123456
  
  3. 点赞分析（使用清洗数据）
     python text_analysis_unified.py like --use-cleaned-data --video-id 123456
  
  4. 情感分析（使用清洗数据）
     python text_analysis_unified.py sentiment --use-cleaned-data --type local --video-id 123456

测试模式示例:
  python text_analysis_unified.py cleaning --test
  python text_analysis_unified.py time --use-cleaned-data --test
  python text_analysis_unified.py like --use-cleaned-data --test
  python text_analysis_unified.py sentiment --use-cleaned-data --type local --test
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='module', help='选择分析模块')
    
    # 情感分析子命令
    sentiment_parser = subparsers.add_parser('sentiment', help='情感分析')
    sentiment_parser.add_argument('--use-cleaned-data', action='store_true', 
                                 help='使用清洗后的数据文件（推荐）')
    sentiment_parser.add_argument('--type', choices=['local', 'aliyun'], 
                                 default='local', help='分析器类型：local(本地词典) 或 aliyun(阿里云API)')
    sentiment_parser.add_argument('--video-id', type=str, help='视频ID，如果不指定则分析所有评论')
    sentiment_parser.add_argument('--limit', type=int, help='限制分析数量')
    sentiment_parser.add_argument('--cleaned-data-path', type=str, help='清洗数据文件路径')
    sentiment_parser.add_argument('--test', action='store_true', help='测试模式，只分析少量数据')
    sentiment_parser.add_argument('--no-save', action='store_true', help='不保存结果文件')
    sentiment_parser.add_argument('--no-report', action='store_true', help='不生成分析报告')
    sentiment_parser.add_argument('--no-viz', action='store_true', help='不创建可视化图表')
    
    # 时间分析子命令
    time_parser = subparsers.add_parser('time', help='从众心理时间分析')
    time_parser.add_argument('--use-cleaned-data', action='store_true', 
                            help='使用清洗后的数据文件（推荐）')
    time_parser.add_argument('--video-id', type=str, help='视频ID，如果不指定则分析所有数据')
    time_parser.add_argument('--limit', type=int, help='限制分析数量')
    time_parser.add_argument('--cleaned-data-path', type=str, help='清洗数据文件路径')
    time_parser.add_argument('--test', action='store_true', help='测试模式，只分析少量数据')
    time_parser.add_argument('--no-save', action='store_true', help='不保存结果文件')
    time_parser.add_argument('--no-report', action='store_true', help='不生成分析报告')
    time_parser.add_argument('--no-viz', action='store_true', help='不创建可视化图表')
    
    # 点赞分析子命令
    like_parser = subparsers.add_parser('like', help='从众心理点赞分析')
    like_parser.add_argument('--use-cleaned-data', action='store_true', 
                            help='使用清洗后的数据文件（推荐）')
    like_parser.add_argument('--video-id', type=str, help='视频ID，如果不指定则分析所有数据')
    like_parser.add_argument('--limit', type=int, help='限制分析数量')
    like_parser.add_argument('--cleaned-data-path', type=str, help='清洗数据文件路径')
    like_parser.add_argument('--test', action='store_true', help='测试模式，只分析少量数据')
    like_parser.add_argument('--no-save', action='store_true', help='不保存结果文件')
    like_parser.add_argument('--no-report', action='store_true', help='不生成分析报告')
    like_parser.add_argument('--no-viz', action='store_true', help='不创建可视化图表')
    
    # 数据清洗子命令
    cleaning_parser = subparsers.add_parser('cleaning', help='数据清洗')
    cleaning_parser.add_argument('--video-id', type=str, help='视频ID，如果不指定则清洗所有数据')
    cleaning_parser.add_argument('--limit', type=int, help='限制清洗数量')
    cleaning_parser.add_argument('--test', action='store_true', help='测试模式，只清洗少量数据')
    cleaning_parser.add_argument('--no-save', action='store_true', help='不保存结果文件')
    cleaning_parser.add_argument('--no-report', action='store_true', help='不生成分析报告')
    cleaning_parser.add_argument('--no-viz', action='store_true', help='不创建可视化图表')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.module:
        parser.print_help()
        return
    
    # 测试模式设置
    if args.test and not args.limit:
        args.limit = 10
        print("🧪 测试模式：只分析少量数据")
    
    # 显示配置信息
    print(f"=== 文本分析统一工具 - {args.module.upper()} 模块 ===")
    if hasattr(args, 'video_id') and args.video_id:
        print(f"视频ID: {args.video_id}")
    if hasattr(args, 'type') and args.type:
        print(f"分析器类型: {args.type}")
    if args.limit:
        print(f"限制数量: {args.limit}")
    if hasattr(args, 'use_cleaned_data') and args.use_cleaned_data:
        print("使用清洗数据")
    print("=" * 50)
    
    # 根据模块调用相应的分析器
    if args.module == 'sentiment':
        run_sentiment_analysis(args)
    elif args.module == 'time':
        run_time_analysis(args)
    elif args.module == 'like':
        run_like_analysis(args)
    elif args.module == 'cleaning':
        run_cleaning_analysis(args)
    else:
        print(f"❌ 未知的分析模块: {args.module}")

def run_sentiment_analysis(args):
    """运行情感分析"""
    try:
        from modules.sentiment_analyzer_optimized import main as sentiment_main
        import sys
        
        # 构建命令行参数
        sys.argv = ['sentiment_analyzer_optimized.py']
        if args.type:
            sys.argv.extend(['--type', args.type])
        if args.video_id:
            sys.argv.extend(['--video-id', args.video_id])
        if args.limit:
            sys.argv.extend(['--limit', str(args.limit)])
        if args.use_cleaned_data:
            sys.argv.append('--use-cleaned-data')
        if args.cleaned_data_path:
            sys.argv.extend(['--cleaned-data-path', args.cleaned_data_path])
        if args.test:
            sys.argv.append('--test')
        if args.no_save:
            sys.argv.append('--no-save')
        if args.no_report:
            sys.argv.append('--no-report')
        if args.no_viz:
            sys.argv.append('--no-viz')
        
        sentiment_main()
        
    except ImportError as e:
        print(f"❌ 导入情感分析模块失败: {e}")
    except Exception as e:
        print(f"❌ 情感分析执行失败: {e}")

def run_time_analysis(args):
    """运行时间分析"""
    try:
        from modules.time_analysis_optimized import main as time_main
        import sys
        
        # 构建命令行参数
        sys.argv = ['time_analysis_optimized.py']
        if args.video_id:
            sys.argv.extend(['--video-id', args.video_id])
        if args.limit:
            sys.argv.extend(['--limit', str(args.limit)])
        if args.use_cleaned_data:
            sys.argv.append('--use-cleaned-data')
        if args.cleaned_data_path:
            sys.argv.extend(['--cleaned-data-path', args.cleaned_data_path])
        if args.test:
            sys.argv.append('--test')
        if args.no_save:
            sys.argv.append('--no-save')
        if args.no_report:
            sys.argv.append('--no-report')
        if args.no_viz:
            sys.argv.append('--no-viz')
        
        time_main()
        
    except ImportError as e:
        print(f"❌ 导入时间分析模块失败: {e}")
    except Exception as e:
        print(f"❌ 时间分析执行失败: {e}")

def run_like_analysis(args):
    """运行点赞分析"""
    try:
        from modules.like_analysis_optimized import main as like_main
        import sys
        
        # 构建命令行参数
        sys.argv = ['like_analysis_optimized.py']
        if args.video_id:
            sys.argv.extend(['--video-id', args.video_id])
        if args.limit:
            sys.argv.extend(['--limit', str(args.limit)])
        if args.use_cleaned_data:
            sys.argv.append('--use-cleaned-data')
        if args.cleaned_data_path:
            sys.argv.extend(['--cleaned-data-path', args.cleaned_data_path])
        if args.test:
            sys.argv.append('--test')
        if args.no_save:
            sys.argv.append('--no-save')
        if args.no_report:
            sys.argv.append('--no-report')
        if args.no_viz:
            sys.argv.append('--no-viz')
        
        like_main()
        
    except ImportError as e:
        print(f"❌ 导入点赞分析模块失败: {e}")
    except Exception as e:
        print(f"❌ 点赞分析执行失败: {e}")

def run_cleaning_analysis(args):
    """运行数据清洗"""
    try:
        from modules.data_cleaning_optimized import main as cleaning_main
        import sys
        
        # 构建命令行参数
        sys.argv = ['data_cleaning_optimized.py']
        if args.video_id:
            sys.argv.extend(['--video-id', args.video_id])
        if args.limit:
            sys.argv.extend(['--limit', str(args.limit)])
        if args.test:
            sys.argv.append('--test')
        if args.no_save:
            sys.argv.append('--no-save')
        if args.no_report:
            sys.argv.append('--no-report')
        if args.no_viz:
            sys.argv.append('--no-viz')
        
        cleaning_main()
        
    except ImportError as e:
        print(f"❌ 导入数据清洗模块失败: {e}")
    except Exception as e:
        print(f"❌ 数据清洗执行失败: {e}")

if __name__ == "__main__":
    main()
