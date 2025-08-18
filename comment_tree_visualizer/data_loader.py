#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论数据加载器
支持从数据库、CSV文件等多种数据源加载评论数据
"""

import os
import json
import pandas as pd
import sqlite3
import pymysql
from typing import Optional, Dict, List, Union
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommentDataLoader:
    """评论数据加载器"""
    
    def __init__(self, data_source: str = "csv"):
        """
        初始化数据加载器
        
        Args:
            data_source: 数据源类型 ("csv", "mysql", "sqlite")
        """
        self.data_source = data_source
        self.connection = None
        
    def load_from_csv(self, file_path: str, encoding: str = "utf-8") -> pd.DataFrame:
        """
        从CSV文件加载评论数据
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            
        Returns:
            DataFrame: 评论数据
        """
        try:
            logger.info(f"从CSV文件加载数据: {file_path}")
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 验证必要的列是否存在
            required_columns = ['comment_id', 'content', 'create_time']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"CSV文件缺少必要的列: {missing_columns}")
            
            # 数据类型转换
            df = self._convert_data_types(df)
            
            logger.info(f"成功加载 {len(df)} 条评论数据")
            return df
            
        except Exception as e:
            logger.error(f"加载CSV文件失败: {e}")
            raise
    
    def load_from_mysql(self, host: str, port: int, user: str, password: str, 
                       database: str, table: str, video_id: Optional[str] = None,
                       limit: Optional[int] = None) -> pd.DataFrame:
        """
        从MySQL数据库加载评论数据
        
        Args:
            host: 数据库主机
            port: 数据库端口
            user: 用户名
            password: 密码
            database: 数据库名
            table: 表名
            video_id: 视频ID（可选）
            limit: 限制加载数量（可选）
            
        Returns:
            DataFrame: 评论数据
        """
        try:
            logger.info(f"连接MySQL数据库: {host}:{port}/{database}")
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4'
            )
            
            # 构建SQL查询
            sql = f"""
            SELECT 
                comment_id, 
                COALESCE(parent_comment_id, '0') as parent_comment_id,
                content, 
                create_time,
                COALESCE(like_count, 0) as like_count,
                COALESCE(sub_comment_count, 0) as sub_comment_count,
                COALESCE(user_id, '') as user_id,
                COALESCE(nickname, '') as nickname
            FROM {table}
            WHERE content IS NOT NULL AND LENGTH(content) > 0
            """
            
            params = []
            if video_id:
                sql += " AND aweme_id = %s"
                params.append(video_id)
                logger.info(f"过滤视频ID: {video_id}")
            
            sql += " ORDER BY create_time ASC"
            
            if limit:
                sql += f" LIMIT {limit}"
                logger.info(f"限制加载数量: {limit}")
            
            # 执行查询
            df = pd.read_sql_query(sql, self.connection, params=params)
            
            # 数据类型转换
            df = self._convert_data_types(df)
            
            logger.info(f"成功加载 {len(df)} 条评论数据")
            return df
            
        except Exception as e:
            logger.error(f"加载MySQL数据失败: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()
    
    def load_from_sqlite(self, db_path: str, table: str, video_id: Optional[str] = None,
                        limit: Optional[int] = None) -> pd.DataFrame:
        """
        从SQLite数据库加载评论数据
        
        Args:
            db_path: 数据库文件路径
            table: 表名
            video_id: 视频ID（可选）
            limit: 限制加载数量（可选）
            
        Returns:
            DataFrame: 评论数据
        """
        try:
            logger.info(f"连接SQLite数据库: {db_path}")
            self.connection = sqlite3.connect(db_path)
            
            # 构建SQL查询
            sql = f"""
            SELECT 
                comment_id, 
                COALESCE(parent_comment_id, '0') as parent_comment_id,
                content, 
                create_time,
                COALESCE(like_count, 0) as like_count,
                COALESCE(sub_comment_count, 0) as sub_comment_count,
                COALESCE(user_id, '') as user_id,
                COALESCE(nickname, '') as nickname
            FROM {table}
            WHERE content IS NOT NULL AND LENGTH(content) > 0
            """
            
            params = []
            if video_id:
                sql += " AND aweme_id = ?"
                params.append(video_id)
                logger.info(f"过滤视频ID: {video_id}")
            
            sql += " ORDER BY create_time ASC"
            
            if limit:
                sql += f" LIMIT {limit}"
                logger.info(f"限制加载数量: {limit}")
            
            # 执行查询
            df = pd.read_sql_query(sql, self.connection, params=params)
            
            # 数据类型转换
            df = self._convert_data_types(df)
            
            logger.info(f"成功加载 {len(df)} 条评论数据")
            return df
            
        except Exception as e:
            logger.error(f"加载SQLite数据失败: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()
    
    def load_from_json(self, file_path: str) -> pd.DataFrame:
        """
        从JSON文件加载评论数据
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            DataFrame: 评论数据
        """
        try:
            logger.info(f"从JSON文件加载数据: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果数据是列表，直接转换为DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            # 如果数据是字典，尝试提取评论列表
            elif isinstance(data, dict):
                if 'comments' in data:
                    df = pd.DataFrame(data['comments'])
                else:
                    raise ValueError("JSON文件格式不正确，应包含comments字段或直接是评论列表")
            else:
                raise ValueError("JSON文件格式不正确")
            
            # 数据类型转换
            df = self._convert_data_types(df)
            
            logger.info(f"成功加载 {len(df)} 条评论数据")
            return df
            
        except Exception as e:
            logger.error(f"加载JSON文件失败: {e}")
            raise
    
    def load_from_processed_data(self, data_dir: str = "data/processed", pattern: str = "*.json", 
                               latest_only: bool = True) -> pd.DataFrame:
        """
        从项目的processed数据目录加载清洗后的评论数据
        
        Args:
            data_dir: 数据目录路径
            pattern: 文件匹配模式
            latest_only: 是否只加载最新的文件
            
        Returns:
            DataFrame: 评论数据
        """
        try:
            import glob
            import os
            
            # 构建完整路径
            if not os.path.isabs(data_dir):
                # 相对于项目根目录
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(project_root, data_dir)
            
            logger.info(f"从processed数据目录加载数据: {data_dir}")
            
            # 查找匹配的文件
            search_pattern = os.path.join(data_dir, pattern)
            files = glob.glob(search_pattern)
            
            if not files:
                raise FileNotFoundError(f"在目录 {data_dir} 中未找到匹配 {pattern} 的文件")
            
            # 按修改时间排序
            files.sort(key=os.path.getmtime, reverse=True)
            
            if latest_only:
                files = [files[0]]  # 只取最新的文件
                logger.info(f"加载最新文件: {os.path.basename(files[0])}")
            else:
                logger.info(f"找到 {len(files)} 个文件，将合并加载")
            
            # 加载所有文件的数据
            all_data = []
            for file_path in files:
                logger.info(f"正在加载文件: {os.path.basename(file_path)}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    all_data.extend(data)
                elif isinstance(data, dict) and 'comments' in data:
                    all_data.extend(data['comments'])
                else:
                    logger.warning(f"跳过格式不正确的文件: {file_path}")
                    continue
            
            if not all_data:
                raise ValueError("没有找到有效的评论数据")
            
            # 转换为DataFrame
            df = pd.DataFrame(all_data)
            
            # 数据类型转换
            df = self._convert_data_types(df)
            
            logger.info(f"成功加载 {len(df)} 条评论数据")
            return df
            
        except Exception as e:
            logger.error(f"加载processed数据失败: {e}")
            raise
    
    def list_processed_files(self, data_dir: str = "data/processed", pattern: str = "*.json") -> List[str]:
        """
        列出processed数据目录中的文件
        
        Args:
            data_dir: 数据目录路径
            pattern: 文件匹配模式
            
        Returns:
            List[str]: 文件路径列表
        """
        try:
            import glob
            import os
            
            # 构建完整路径
            if not os.path.isabs(data_dir):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(project_root, data_dir)
            
            search_pattern = os.path.join(data_dir, pattern)
            files = glob.glob(search_pattern)
            
            # 按修改时间排序
            files.sort(key=os.path.getmtime, reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"列出processed文件失败: {e}")
            return []
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        转换数据类型
        
        Args:
            df: 原始DataFrame
            
        Returns:
            DataFrame: 转换后的DataFrame
        """
        df = df.copy()
        
        # 确保comment_id和parent_comment_id为字符串类型
        if 'comment_id' in df.columns:
            df['comment_id'] = df['comment_id'].astype(str)
        if 'parent_comment_id' in df.columns:
            df['parent_comment_id'] = df['parent_comment_id'].astype(str)
        
        # 转换数值类型
        if 'like_count' in df.columns:
            df['like_count'] = pd.to_numeric(df['like_count'], errors='coerce').fillna(0).astype(int)
        if 'sub_comment_count' in df.columns:
            df['sub_comment_count'] = pd.to_numeric(df['sub_comment_count'], errors='coerce').fillna(0).astype(int)
        if 'create_time' in df.columns:
            df['create_time'] = pd.to_numeric(df['create_time'], errors='coerce')
        
        # 确保文本字段为字符串
        text_columns = ['content', 'user_id', 'nickname']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, file_path: str, encoding: str = "utf-8"):
        """
        保存数据到CSV文件
        
        Args:
            df: 评论数据
            file_path: 保存路径
            encoding: 文件编码
        """
        try:
            logger.info(f"保存数据到CSV文件: {file_path}")
            df.to_csv(file_path, index=False, encoding=encoding)
            logger.info("数据保存成功")
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
            raise
    
    def save_to_json(self, df: pd.DataFrame, file_path: str):
        """
        保存数据到JSON文件
        
        Args:
            df: 评论数据
            file_path: 保存路径
        """
        try:
            logger.info(f"保存数据到JSON文件: {file_path}")
            data = {
                'metadata': {
                    'total_comments': len(df),
                    'export_time': datetime.now().isoformat(),
                    'columns': list(df.columns)
                },
                'comments': df.to_dict('records')
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info("数据保存成功")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            raise
