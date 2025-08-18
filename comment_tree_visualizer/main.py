#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论树可视化主程序
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from data_loader import CommentDataLoader
from tree_builder import CommentTreeBuilder
from visualizer import CommentTreeVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="评论树可视化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --source processed --output output_dir
  python main.py --source csv --input data.csv --output output_dir
  python main.py --source mysql --output output_dir --title "我的评论树"
        """
    )
    
    # 数据源参数
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        choices=['csv', 'json', 'mysql', 'sqlite', 'processed'],
        help='数据源类型: csv, json, mysql, sqlite, processed'
    )
    
    # 输入文件参数
    parser.add_argument(
        '--input',
        type=str,
        help='输入文件路径 (用于csv和json数据源)'
    )
    
    # 输出目录参数
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='输出目录路径 (默认: output)'
    )
    
    # 页面标题参数
    parser.add_argument(
        '--title',
        type=str,
        default='评论树可视化',
        help='页面标题 (默认: 评论树可视化)'
    )
    
    # 最大深度参数
    parser.add_argument(
        '--max-depth',
        type=int,
        default=5,
        help='最大显示深度 (默认: 5)'
    )
    
    # 数据库配置参数
    parser.add_argument(
        '--db-host',
        type=str,
        default='localhost',
        help='数据库主机 (默认: localhost)'
    )
    
    parser.add_argument(
        '--db-port',
        type=int,
        default=3306,
        help='数据库端口 (默认: 3306)'
    )
    
    parser.add_argument(
        '--db-name',
        type=str,
        help='数据库名称'
    )
    
    parser.add_argument(
        '--db-user',
        type=str,
        help='数据库用户名'
    )
    
    parser.add_argument(
        '--db-password',
        type=str,
        help='数据库密码'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    try:
        # 创建数据加载器
        loader = CommentDataLoader()
        
        # 根据数据源类型加载数据
        if args.source == 'processed':
            logger.info(f"从processed数据目录生成评论树可视化: data/processed")
            df = loader.load_from_processed_data()
        elif args.source == 'csv':
            if not args.input:
                raise ValueError("CSV数据源需要指定 --input 参数")
            df = loader.load_from_csv(args.input)
        elif args.source == 'json':
            if not args.input:
                raise ValueError("JSON数据源需要指定 --input 参数")
            df = loader.load_from_json(args.input)
        elif args.source == 'mysql':
            if not all([args.db_name, args.db_user, args.db_password]):
                raise ValueError("MySQL数据源需要指定 --db-name, --db-user, --db-password 参数")
            df = loader.load_from_mysql(
                host=args.db_host,
                port=args.db_port,
                database=args.db_name,
                user=args.db_user,
                password=args.db_password
            )
        elif args.source == 'sqlite':
            if not args.input:
                raise ValueError("SQLite数据源需要指定 --input 参数")
            df = loader.load_from_sqlite(args.input)
        else:
            raise ValueError(f"不支持的数据源类型: {args.source}")
        
        # 构建评论树
        builder = CommentTreeBuilder()
        builder.build_tree(df, max_depth=args.max_depth)
        
        # 获取JSON数据
        tree_data = json.loads(builder.to_json())
        
        # 创建可视化器
        visualizer = CommentTreeVisualizer(tree_data)
        
        # 生成输出目录
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成可视化文件
        html_path = output_dir / 'comment_tree_visualization.html'
        simple_html_path = output_dir / 'comment_tree_simple.html'
        json_path = output_dir / 'comment_tree_data.json'
        
        # 生成HTML可视化页面
        visualizer.generate_html(str(html_path), args.title)
        
        # 生成简化版HTML页面
        visualizer.generate_simple_html(str(simple_html_path), args.title)
        
        # 保存JSON数据
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=2)
        
        # 输出结果
        logger.info("可视化文件已生成:")
        logger.info(f"  - 完整版HTML: {html_path}")
        logger.info(f"  - 简化版HTML: {simple_html_path}")
        logger.info(f"  - JSON数据: {json_path}")
        
        print(f"\n✅ 评论树可视化生成完成！")
        print(f"📁 输出目录: {output_dir.absolute()}")
        print(f"🌐 打开 {html_path} 查看交互式可视化")
        print(f"📄 打开 {simple_html_path} 查看简化版可视化")
        
    except Exception as e:
        logger.error(f"生成评论树可视化时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
