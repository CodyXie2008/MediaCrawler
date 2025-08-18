#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论树构建器
将评论数据转换为树形结构，支持多层级评论关系
"""

import pandas as pd
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CommentNode:
    """评论节点类"""
    
    def __init__(self, comment_id: str, content: str, **kwargs):
        self.comment_id = comment_id
        self.content = content
        self.children = []
        self.parent = None
        
        # 其他属性
        self.create_time = kwargs.get('create_time', 0)
        self.like_count = kwargs.get('like_count', 0)
        self.sub_comment_count = kwargs.get('sub_comment_count', 0)
        self.user_id = kwargs.get('user_id', '')
        self.nickname = kwargs.get('nickname', '')
        
        # 计算属性
        self.depth = 0
        self.total_children = 0
        self.total_likes = 0
        
    def add_child(self, child_node):
        """添加子节点"""
        child_node.parent = self
        child_node.depth = self.depth + 1
        self.children.append(child_node)
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.comment_id,
            'content': self.content,
            'create_time': self.create_time,
            'like_count': self.like_count,
            'sub_comment_count': self.sub_comment_count,
            'user_id': self.user_id,
            'nickname': self.nickname,
            'depth': self.depth,
            'total_children': self.total_children,
            'total_likes': self.total_likes,
            'children': [child.to_dict() for child in self.children]
        }
    
    def __str__(self):
        return f"CommentNode(id={self.comment_id}, content='{self.content[:20]}...', children={len(self.children)})"

class CommentTreeBuilder:
    """评论树构建器"""
    
    def __init__(self):
        self.comments_df = None
        self.root_nodes = []
        self.node_map = {}
        
    def build_tree(self, comments_df: pd.DataFrame, max_depth: int = 5) -> List[CommentNode]:
        """
        构建评论树
        
        Args:
            comments_df: 评论数据DataFrame
            max_depth: 最大深度限制
            
        Returns:
            List[CommentNode]: 根节点列表
        """
        logger.info("开始构建评论树...")
        
        self.comments_df = comments_df.copy()
        self.root_nodes = []
        self.node_map = {}
        
        # 数据预处理
        self._preprocess_data()
        
        # 构建节点映射
        self._build_node_map()
        
        # 构建父子关系
        self._build_parent_child_relationships()
        
        # 计算统计信息
        self._calculate_statistics()
        
        # 过滤深度
        if max_depth > 0:
            self._filter_by_depth(max_depth)
        
        logger.info(f"评论树构建完成，共 {len(self.root_nodes)} 个根节点")
        return self.root_nodes
    
    def _preprocess_data(self):
        """数据预处理"""
        logger.info("数据预处理...")
        
        # 确保必要的列存在
        required_columns = ['comment_id', 'content', 'parent_comment_id']
        missing_columns = [col for col in required_columns if col not in self.comments_df.columns]
        
        if missing_columns:
            raise ValueError(f"缺少必要的列: {missing_columns}")
        
        # 处理缺失值
        self.comments_df['parent_comment_id'] = self.comments_df['parent_comment_id'].fillna('0')
        self.comments_df['content'] = self.comments_df['content'].fillna('')
        
        # 过滤空内容
        self.comments_df = self.comments_df[self.comments_df['content'].str.strip() != '']
        
        # 确保ID为字符串类型
        self.comments_df['comment_id'] = self.comments_df['comment_id'].astype(str)
        self.comments_df['parent_comment_id'] = self.comments_df['parent_comment_id'].astype(str)
        
        logger.info(f"预处理完成，有效评论数: {len(self.comments_df)}")
    
    def _build_node_map(self):
        """构建节点映射"""
        logger.info("构建节点映射...")
        
        for _, row in self.comments_df.iterrows():
            node = CommentNode(
                comment_id=row['comment_id'],
                content=row['content'],
                create_time=row.get('create_time', 0),
                like_count=row.get('like_count', 0),
                sub_comment_count=row.get('sub_comment_count', 0),
                user_id=row.get('user_id', ''),
                nickname=row.get('nickname', '')
            )
            self.node_map[row['comment_id']] = node
    
    def _build_parent_child_relationships(self):
        """构建父子关系"""
        logger.info("构建父子关系...")
        
        for _, row in self.comments_df.iterrows():
            comment_id = row['comment_id']
            parent_id = row['parent_comment_id']
            
            current_node = self.node_map.get(comment_id)
            if not current_node:
                continue
            
            # 如果是根评论
            if parent_id == '0' or parent_id not in self.node_map:
                self.root_nodes.append(current_node)
            else:
                # 添加为子评论
                parent_node = self.node_map.get(parent_id)
                if parent_node:
                    parent_node.add_child(current_node)
                else:
                    # 父节点不存在，作为根节点处理
                    self.root_nodes.append(current_node)
    
    def _calculate_statistics(self):
        """计算统计信息"""
        logger.info("计算统计信息...")
        
        def calculate_node_stats(node: CommentNode):
            """递归计算节点统计信息"""
            total_children = len(node.children)
            total_likes = node.like_count
            
            for child in node.children:
                child_stats = calculate_node_stats(child)
                total_children += child_stats['total_children']
                total_likes += child_stats['total_likes']
            
            node.total_children = total_children
            node.total_likes = total_likes
            
            return {
                'total_children': total_children,
                'total_likes': total_likes
            }
        
        # 为每个根节点计算统计信息
        for root_node in self.root_nodes:
            calculate_node_stats(root_node)
    
    def _filter_by_depth(self, max_depth: int):
        """按深度过滤"""
        logger.info(f"按深度过滤，最大深度: {max_depth}")
        
        def filter_node(node: CommentNode, current_depth: int = 0):
            """递归过滤节点"""
            if current_depth >= max_depth:
                node.children = []
                return
            
            for child in node.children:
                filter_node(child, current_depth + 1)
        
        for root_node in self.root_nodes:
            filter_node(root_node)
    
    def get_tree_statistics(self) -> Dict[str, Any]:
        """获取树形结构统计信息"""
        if not self.root_nodes:
            return {}
        
        total_nodes = len(self.node_map)
        total_roots = len(self.root_nodes)
        
        # 计算最大深度
        max_depth = 0
        for root in self.root_nodes:
            max_depth = max(max_depth, self._get_node_depth(root))
        
        # 计算平均子节点数
        total_children = sum(len(root.children) for root in self.root_nodes)
        avg_children = total_children / total_roots if total_roots > 0 else 0
        
        # 计算点赞统计
        total_likes = sum(node.like_count for node in self.node_map.values())
        avg_likes = total_likes / total_nodes if total_nodes > 0 else 0
        
        return {
            'total_nodes': total_nodes,
            'total_roots': total_roots,
            'max_depth': max_depth,
            'avg_children_per_root': avg_children,
            'total_likes': total_likes,
            'avg_likes_per_comment': avg_likes
        }
    
    def _get_node_depth(self, node: CommentNode) -> int:
        """获取节点深度"""
        if not node.children:
            return 0
        return 1 + max(self._get_node_depth(child) for child in node.children)
    
    def to_json(self, file_path: str = None) -> str:
        """转换为JSON格式"""
        tree_data = {
            'metadata': {
                'generated_time': datetime.now().isoformat(),
                'statistics': self.get_tree_statistics()
            },
            'nodes': [root.to_dict() for root in self.root_nodes]
        }
        
        json_str = json.dumps(tree_data, ensure_ascii=False, indent=2)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"树形数据已保存到: {file_path}")
        
        return json_str
    
    def find_node_by_id(self, comment_id: str) -> Optional[CommentNode]:
        """根据评论ID查找节点"""
        return self.node_map.get(comment_id)
    
    def find_nodes_by_user(self, user_id: str) -> List[CommentNode]:
        """根据用户ID查找节点"""
        return [node for node in self.node_map.values() if node.user_id == user_id]
    
    def get_hot_comments(self, top_n: int = 10) -> List[CommentNode]:
        """获取热门评论（按点赞数排序）"""
        sorted_nodes = sorted(
            self.node_map.values(), 
            key=lambda x: x.like_count, 
            reverse=True
        )
        return sorted_nodes[:top_n]
    
    def get_deepest_threads(self, top_n: int = 5) -> List[CommentNode]:
        """获取最深的评论线程"""
        def get_thread_depth(node: CommentNode) -> int:
            if not node.children:
                return 0
            return 1 + max(get_thread_depth(child) for child in node.children)
        
        sorted_roots = sorted(
            self.root_nodes,
            key=get_thread_depth,
            reverse=True
        )
        return sorted_roots[:top_n]
