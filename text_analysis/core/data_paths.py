"""
数据存储路径配置文件
统一管理text_analysis模块的所有数据存储路径
"""

import os
from pathlib import Path
from datetime import datetime

# 获取项目根目录 - 指向MediaCrawler项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据目录结构
DATA_DIRS = {
    'raw': PROJECT_ROOT / 'data' / 'raw',                    # 原始数据
    'processed': PROJECT_ROOT / 'data' / 'processed',        # 处理后数据
    'results': PROJECT_ROOT / 'data' / 'results',            # 分析结果
    'visualizations': PROJECT_ROOT / 'data' / 'visualizations', # 可视化图表
    'reports': PROJECT_ROOT / 'data' / 'reports',            # 分析报告
    'temp': PROJECT_ROOT / 'data' / 'temp'                   # 临时文件
}

# 确保目录存在
def ensure_directories():
    """确保所有数据目录都存在"""
    for dir_path in DATA_DIRS.values():
        dir_path.mkdir(parents=True, exist_ok=True)

# 获取文件路径
def get_data_path(category: str, filename: str) -> str:
    """获取指定类别的数据文件路径"""
    if category not in DATA_DIRS:
        raise ValueError(f"未知的数据类别: {category}")
    
    return str(DATA_DIRS[category] / filename)

# 生成带时间戳的文件名
def get_timestamped_filename(prefix: str, suffix: str = '.json') -> str:
    """生成带时间戳的文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{suffix}"

# 常用文件路径
COMMON_PATHS = {
    'processed_comments': get_data_path('processed', 'douyin_comments_processed.json'),
    'stopwords': PROJECT_ROOT / 'docs' / 'hit_stopwords.txt'
}

# 模块特定的路径生成函数
class PathManager:
    """路径管理器"""
    
    @staticmethod
    def get_sentiment_analysis_paths():
        """获取情感分析模块的路径"""
        timestamp = get_timestamped_filename('sentiment_analysis', '')
        return {
            'results_csv': get_data_path('results', f'sentiment_analysis_results_{timestamp}.csv'),
            'results_json': get_data_path('results', f'sentiment_analysis_results_{timestamp}.json'),
            'report': get_data_path('reports', f'sentiment_analysis_report_{timestamp}.json'),
            'visualization': get_data_path('visualizations', 'sentiment_analysis_visualization.png')
        }
    
    @staticmethod
    def get_time_analysis_paths():
        """获取时间分析模块的路径"""
        timestamp = get_timestamped_filename('time_analysis', '')
        return {
            'report': get_data_path('reports', f'time_analysis_report_{timestamp}.json'),
            'visualization': get_data_path('visualizations', f'time_analysis_visualization_{timestamp}.png')
        }
    
    @staticmethod
    def get_like_analysis_paths():
        """获取点赞分析模块的路径"""
        timestamp = get_timestamped_filename('like_analysis', '')
        return {
            'report': get_data_path('reports', f'like_analysis_report_{timestamp}.json'),
            'visualization': get_data_path('visualizations', f'like_analysis_visualization_{timestamp}.png')
        }
    
    @staticmethod
    def get_data_cleaning_paths():
        """获取数据清洗模块的路径"""
        timestamp = get_timestamped_filename('data_cleaning', '')
        return {
            'processed_data': get_data_path('processed', f'cleaned_data_{timestamp}.json'),
            'cleaning_report': get_data_path('reports', f'cleaning_report_{timestamp}.json')
        }
    
    @staticmethod
    def get_conformity_analysis_paths():
        """获取从众心理综合分析路径"""
        timestamp = get_timestamped_filename('conformity_analysis', '')
        return {
            'comprehensive_report': get_data_path('reports', f'conformity_comprehensive_report_{timestamp}.json'),
            'summary_visualization': get_data_path('visualizations', f'conformity_summary_{timestamp}.png')
        }

# 便捷函数
def get_sentiment_analysis_paths():
    """获取情感分析模块的路径（向后兼容）"""
    return PathManager.get_sentiment_analysis_paths()

def get_conformity_time_paths():
    """获取从众时间分析模块的路径（向后兼容）"""
    return PathManager.get_time_analysis_paths()

def get_like_interaction_paths():
    """获取点赞互动分析模块的路径（向后兼容）"""
    return PathManager.get_like_analysis_paths()

# 初始化时确保目录存在
ensure_directories() 