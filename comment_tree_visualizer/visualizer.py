#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论树可视化器
生成交互式HTML可视化页面，支持D3.js树形图展示
"""

import os
import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CommentTreeVisualizer:
    """评论树可视化器"""
    
    def __init__(self, tree_data: Dict[str, Any]):
        """
        初始化可视化器
        
        Args:
            tree_data: 树形数据（JSON格式）
        """
        self.tree_data = tree_data
        
    def generate_html(self, output_path: str, title: str = "评论树可视化") -> str:
        """
        生成交互式HTML可视化页面
        
        Args:
            output_path: 输出文件路径
            title: 页面标题
            
        Returns:
            str: 生成的HTML内容
        """
        logger.info(f"生成HTML可视化页面: {output_path}")
        
        # 生成HTML内容
        html_content = self._generate_html_content(title)
        
        # 保存到文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML页面已生成: {output_path}")
        return html_content
    
    def _generate_html_content(self, title: str) -> str:
        """生成HTML内容"""
        # 将JSON数据转换为字符串，避免f-string中的语法问题
        json_data = json.dumps(self.tree_data, ensure_ascii=False, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        
        .header h1 {{
            color: #333;
            margin: 0 0 10px 0;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            margin: 5px;
            min-width: 120px;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .controls {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .control-group {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .control-group label {{
            font-size: 14px;
            color: #555;
        }}
        
        .control-group input, .control-group select {{
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        
        .control-group button {{
            padding: 5px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .control-group button:hover {{
            background-color: #0056b3;
        }}
        
        .visualization {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            background-color: white;
            min-height: 600px;
        }}
        
        .node {{
            cursor: pointer;
        }}
        
        .node circle {{
            fill: #fff;
            stroke: #007bff;
            stroke-width: 2px;
        }}
        
        .node text {{
            font: 12px sans-serif;
        }}
        
        .link {{
            fill: none;
            stroke: #ccc;
            stroke-width: 1px;
        }}
        
        .tooltip {{
            position: absolute;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
        }}
        
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        
        .legend h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>交互式评论树可视化 - 展示评论的层级关系和互动情况</p>
        </div>
        
        <div class="stats" id="stats">
            <!-- 统计信息将通过JavaScript动态生成 -->
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>搜索:</label>
                <input type="text" id="searchInput" placeholder="输入评论内容或用户名...">
                <button onclick="searchComments()">搜索</button>
            </div>
            
            <div class="control-group">
                <label>节点大小:</label>
                <select id="sizeSelect" onchange="updateNodeSize()">
                    <option value="likes">按点赞数</option>
                    <option value="replies" selected>按回复数</option>
                    <option value="fixed">固定大小</option>
                </select>
            </div>
            
            <div class="control-group">
                <button onclick="resetView()">重置视图</button>
            </div>
        </div>
        
        <div class="visualization" id="visualization">
            <!-- 可视化内容将在这里渲染 -->
        </div>
        
        <div class="legend">
            <h3>图例说明</h3>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #6c757d;"></div>
                <span>虚拟根节点</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #007bff;"></div>
                <span>根评论</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #28a745;"></div>
                <span>子评论</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #ffc107;"></div>
                <span>高点赞评论</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #dc3545;"></div>
                <span>热门评论</span>
            </div>
        </div>
    </div>

    <script>
        // 评论数据
        const commentData = {json_data};
        
        // 可视化配置
        let config = {{
            width: 1200,
            height: 600,
            nodeRadius: 8,
            nodeSpacing: 100,
            levelSpacing: 150
        }};
        
        // 当前搜索状态
        let searchResults = [];
        let currentSearchTerm = '';
        
        // 初始化可视化
        function initVisualization() {{
            updateStats();
            renderTree();
        }}
        
        // 更新统计信息
        function updateStats() {{
            const stats = commentData.metadata.statistics;
            const statsContainer = document.getElementById('stats');
            
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <div class="stat-value">${{stats.total_nodes}}</div>
                    <div class="stat-label">总评论数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${{stats.total_roots}}</div>
                    <div class="stat-label">根评论数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${{stats.max_depth}}</div>
                    <div class="stat-label">最大深度</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${{stats.total_likes}}</div>
                    <div class="stat-label">总点赞数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${{stats.avg_likes_per_comment.toFixed(1)}}</div>
                    <div class="stat-label">平均点赞数</div>
                </div>
            `;
        }}
        
        // 渲染树形图
        function renderTree() {{
            const container = document.getElementById('visualization');
            container.innerHTML = '';
            
            const svg = d3.select(container)
                .append('svg')
                .attr('width', config.width)
                .attr('height', config.height)
                .style('border', '1px solid #ddd');
            
            // 创建树形布局
            const tree = d3.tree()
                .size([config.height - 100, config.width - 200])
                .nodeSize([config.nodeSpacing, config.levelSpacing]);
            
            // 创建虚拟根节点来连接所有根评论
            const virtualRoot = {{
                id: 'virtual_root',
                content: '所有评论',
                children: commentData.nodes
            }};
            
            // 创建层次结构
            const root = d3.hierarchy(virtualRoot);
            const treeData = tree(root);
            
            // 创建连接线
            const links = svg.selectAll('.link')
                .data(treeData.links())
                .enter()
                .append('path')
                .attr('class', 'link')
                .attr('d', d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x));
            
            // 创建节点
            const nodes = svg.selectAll('.node')
                .data(treeData.descendants())
                .enter()
                .append('g')
                .attr('class', 'node')
                .attr('transform', d => `translate(${{d.y}},${{d.x}})`);
            
            // 添加节点圆圈
            nodes.append('circle')
                .attr('r', d => getNodeRadius(d))
                .style('fill', d => getNodeColor(d))
                .style('stroke', '#333')
                .style('stroke-width', 2)
                .on('mouseover', showTooltip)
                .on('mouseout', hideTooltip)
                .on('click', toggleNode);
            
            // 添加节点文本
            nodes.append('text')
                .attr('dy', '.35em')
                .attr('x', d => d.children ? -10 : 10)
                .style('text-anchor', d => d.children ? 'end' : 'start')
                .style('font-size', '10px')
                .text(d => getNodeText(d));
        }}
        
        // 获取节点半径
        function getNodeRadius(d) {{
            // 虚拟根节点
            if (d.data.id === 'virtual_root') return 15;
            
            const sizeType = document.getElementById('sizeSelect').value;
            
            switch(sizeType) {{
                case 'likes':
                    return Math.max(5, Math.min(20, d.data.like_count / 10 + 5));
                case 'replies':
                    return Math.max(5, Math.min(20, d.data.total_children / 5 + 5));
                case 'fixed':
                    return config.nodeRadius;
                default:
                    return config.nodeRadius;
            }}
        }}
        
        // 获取节点颜色
        function getNodeColor(d) {{
            // 虚拟根节点
            if (d.data.id === 'virtual_root') return '#6c757d';  // 灰色
            
            if (d.data.like_count > 50) return '#dc3545';  // 热门评论（红色）
            if (d.data.like_count > 20) return '#ffc107';  // 高点赞（黄色）
            if (d.depth === 1) return '#007bff';           // 根评论（蓝色）
            return '#28a745';                              // 子评论（绿色）
        }}
        
        // 获取节点文本
        function getNodeText(d) {{
            // 虚拟根节点
            if (d.data.id === 'virtual_root') return '所有评论';
            
            const content = d.data.content;
            const maxLength = 15;
            return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
        }}
        
        // 显示工具提示
        function showTooltip(event, d) {{
            const tooltip = d3.select('body').append('div')
                .attr('class', 'tooltip')
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
            
            // 虚拟根节点
            if (d.data.id === 'virtual_root') {{
                tooltip.html(`
                    <strong>虚拟根节点</strong><br>
                    包含所有根评论
                `);
            }} else {{
                tooltip.html(`
                    <strong>评论内容:</strong><br>
                    ${{d.data.content}}<br><br>
                    <strong>用户:</strong> ${{d.data.nickname || '匿名'}}<br>
                    <strong>点赞数:</strong> ${{d.data.like_count}}<br>
                    <strong>回复数:</strong> ${{d.data.total_children}}<br>
                    <strong>深度:</strong> ${{d.data.depth}}<br>
                    <strong>时间:</strong> ${{formatTime(d.data.create_time)}}
                `);
            }}
        }}
        
        // 隐藏工具提示
        function hideTooltip() {{
            d3.selectAll('.tooltip').remove();
        }}
        
        // 切换节点展开/收起
        function toggleNode(event, d) {{
            if (d.children) {{
                d._children = d.children;
                d.children = null;
            }} else {{
                d.children = d._children;
                d._children = null;
            }}
            renderTree();
        }}
        
        // 搜索评论
        function searchComments() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            currentSearchTerm = searchTerm;
            
            if (!searchTerm) {{
                clearSearch();
                return;
            }}
            
            searchResults = [];
            // 在所有根节点中搜索
            commentData.nodes.forEach(node => {{
                searchInTree(node, searchTerm)
            }})
            
            if (searchResults.length > 0) {{
                alert(`找到 ${{searchResults.length}} 条匹配的评论`);
            }} else {{
                alert('未找到匹配的评论');
            }}
        }}
        
        // 在树中搜索
        function searchInTree(node, searchTerm) {{
            if (node.content.toLowerCase().includes(searchTerm) || 
                (node.nickname && node.nickname.toLowerCase().includes(searchTerm))) {{
                searchResults.push(node);
            }}
            
            if (node.children) {{
                node.children.forEach(child => searchInTree(child, searchTerm));
            }}
        }}
        
        // 清除搜索
        function clearSearch() {{
            searchResults = [];
            currentSearchTerm = '';
        }}
        
        // 更新节点大小
        function updateNodeSize() {{
            renderTree();
        }}
        
        // 重置视图
        function resetView() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('sizeSelect').value = 'replies';
            clearSearch();
            renderTree();
        }}
        
        // 格式化时间
        function formatTime(timestamp) {{
            if (!timestamp) return '未知时间';
            const date = new Date(timestamp * 1000);
            return date.toLocaleString('zh-CN');
        }}
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            initVisualization();
        }});
    </script>
</body>
</html>"""
    
    def generate_simple_html(self, output_path: str, title: str = "评论树可视化") -> str:
        """
        生成简化版HTML可视化页面（不依赖外部库）
        
        Args:
            output_path: 输出文件路径
            title: 页面标题
            
        Returns:
            str: 生成的HTML内容
        """
        logger.info(f"生成简化版HTML可视化页面: {output_path}")
        
        # 生成简化版HTML内容
        html_content = self._generate_simple_html_content(title)
        
        # 保存到文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"简化版HTML页面已生成: {output_path}")
        return html_content
    
    def _generate_simple_html_content(self, title: str) -> str:
        """生成简化版HTML内容"""
        # 将JSON数据转换为字符串
        json_data = json.dumps(self.tree_data, ensure_ascii=False, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        
        .header h1 {{
            color: #333;
            margin: 0 0 10px 0;
        }}
        
        .comment-tree {{
            font-family: monospace;
            line-height: 1.6;
        }}
        
        .comment-node {{
            margin: 5px 0;
            padding: 10px;
            border-left: 3px solid #007bff;
            background-color: #f8f9fa;
            border-radius: 0 5px 5px 0;
        }}
        
        .comment-content {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .comment-meta {{
            font-size: 12px;
            color: #666;
        }}
        
        .comment-children {{
            margin-left: 30px;
            border-left: 1px solid #ddd;
            padding-left: 15px;
        }}
        
        .hot-comment {{
            border-left-color: #dc3545;
            background-color: #fff5f5;
        }}
        
        .high-like-comment {{
            border-left-color: #ffc107;
            background-color: #fffbf0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>评论树结构展示</p>
        </div>
        
        <div class="comment-tree" id="commentTree">
            <!-- 评论树内容将通过JavaScript生成 -->
        </div>
    </div>

    <script>
        // 评论数据
        const commentData = {json_data};
        
        // 渲染评论树
        function renderCommentTree() {{
            const container = document.getElementById('commentTree');
            container.innerHTML = '';
            
            commentData.nodes.forEach((node, index) => {{
                const nodeElement = createCommentNode(node, 0);
                container.appendChild(nodeElement);
            }});
        }}
        
        // 创建评论节点元素
        function createCommentNode(node, depth) {{
            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'comment-node';
            
            // 根据点赞数添加样式类
            if (node.like_count > 50) {{
                nodeDiv.classList.add('hot-comment');
            }} else if (node.like_count > 20) {{
                nodeDiv.classList.add('high-like-comment');
            }}
            
            // 添加缩进
            nodeDiv.style.marginLeft = (depth * 20) + 'px';
            
            // 评论内容
            const contentDiv = document.createElement('div');
            contentDiv.className = 'comment-content';
            contentDiv.textContent = node.content;
            nodeDiv.appendChild(contentDiv);
            
            // 评论元信息
            const metaDiv = document.createElement('div');
            metaDiv.className = 'comment-meta';
            metaDiv.innerHTML = `
                用户: ${{node.nickname || '匿名'}} | 
                点赞: ${{node.like_count}} | 
                回复: ${{node.total_children}} | 
                时间: ${{formatTime(node.create_time)}}
            `;
            nodeDiv.appendChild(metaDiv);
            
            // 子评论
            if (node.children && node.children.length > 0) {{
                const childrenDiv = document.createElement('div');
                childrenDiv.className = 'comment-children';
                
                node.children.forEach(child => {{
                    const childElement = createCommentNode(child, depth + 1);
                    childrenDiv.appendChild(childElement);
                }});
                
                nodeDiv.appendChild(childrenDiv);
            }}
            
            return nodeDiv;
        }}
        
        // 格式化时间
        function formatTime(timestamp) {{
            if (!timestamp) return '未知时间';
            const date = new Date(timestamp * 1000);
            return date.toLocaleString('zh-CN');
        }}
        
        // 页面加载完成后渲染
        document.addEventListener('DOMContentLoaded', function() {{
            renderCommentTree();
        }});
    </script>
</body>
</html>"""
