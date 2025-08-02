#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音评论数据准备与清洗完整流程
包含：数据准备阶段 + 数据清洗阶段
"""

import sys
import os
import re
import json
from datetime import datetime, timedelta
sys.path.append('..')

import pandas as pd
import jieba
from config.db_config import get_db_conn

class CommentDataProcessor:
    def __init__(self):
        self.stop_words = self.load_stop_words()
        
    def load_stop_words(self):
        """加载停用词"""
        stop_words = set()
        try:
            # 尝试加载项目自带的停用词文件
            stop_words_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'hit_stopwords.txt')
            if os.path.exists(stop_words_file):
                with open(stop_words_file, 'r', encoding='utf-8') as f:
                    stop_words = set(line.strip() for line in f if line.strip())
            else:
                # 使用基础停用词
                stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        except Exception as e:
            print(f"加载停用词失败: {e}")
            stop_words = set()
        return stop_words
    
    def is_spam_comment(self, content, user_signature=None):
        """判断是否为垃圾评论"""
        if not content:
            return True
        
        # 内容长度检查
        if len(content.strip()) < 5:
            return True
        
        # 特殊字符比例检查 - 提高阈值，避免误过滤表情符号
        special_char_ratio = len(re.findall(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', content)) / len(content)
        if special_char_ratio > 0.6:  # 提高到60%，避免误过滤正常表情符号
            return True
        
        # 广告关键词检查
        ad_keywords = [
            '加微信', '加qq', '加群', '私信', '联系我', '合作', '推广', '广告',
            '赚钱', '兼职', '代理', '加盟', '招商', '投资', '理财', '贷款',
            '免费领取', '限时优惠', '点击链接', '扫码关注', '关注公众号'
        ]
        content_lower = content.lower()
        for keyword in ad_keywords:
            if keyword in content_lower:
                return True
        
        # 重复字符检查 - 提高阈值
        if len(set(content)) < len(content) * 0.2:  # 降低到20%，避免误过滤
            return True
        
        # 用户签名检查
        if user_signature:
            if len(user_signature) > 100:
                return True
            if re.search(r'[0-9]{8,}', user_signature):
                return True
        
        return False
    
    def clean_text(self, text):
        """文本清洗"""
        if not text:
            return ""
        
        # 1. 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 2. 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 3. 去除方括号内容（如[666][比心]等）
        text = re.sub(r'\[[^\]]*\]', '', text)
        
        # 4. 去除多余空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 5. 保留中文、英文、数字、中文标点，去除其他符号
        # 中文标点范围：\u3000-\u303f (全角字符)
        # 中文标点范围：\uff00-\uffef (全角字符)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\u3000-\u303f\uff00-\uffef]', '', text)
        
        return text
    
    def segment_text(self, text):
        """中文分词"""
        if not text:
            return []
        
        # 使用jieba分词
        words = jieba.lcut(text)
        
        # 去除停用词
        words = [word for word in words if word not in self.stop_words and len(word.strip()) > 0]
        
        return words
    
    def get_raw_comments(self, conn, start_time=None, end_time=None):
        """获取原始评论数据（不进行任何过滤）"""
        base_sql = """
        SELECT 
            comment_id, aweme_id, parent_comment_id, content, create_time, 
            like_count, sub_comment_count, user_id, nickname, user_signature
        FROM douyin_aweme_comment
        WHERE content IS NOT NULL
        """
        
        # 添加时间过滤（可选）
        if start_time:
            start_timestamp = int(start_time.timestamp())
            base_sql += f" AND create_time >= {start_timestamp}"
        
        if end_time:
            end_timestamp = int(end_time.timestamp())
            base_sql += f" AND create_time <= {end_timestamp}"
        
        print(f"执行SQL查询: {base_sql}")
        
        # 读取数据
        df = pd.read_sql_query(base_sql, conn)
        print(f"原始数据量: {len(df)} 条")
        
        # 数据质量检查
        self.check_data_quality(df)
        
        return df
    
    def get_filtered_comments(self, conn, start_time=None, end_time=None, min_likes=0, min_sub_comments=0):
        """获取过滤后的评论数据（保留原有功能作为备选）"""
        base_sql = """
        SELECT 
            comment_id, aweme_id, parent_comment_id, content, create_time, 
            like_count, sub_comment_count, user_id, nickname, user_signature
        FROM douyin_aweme_comment
        WHERE content IS NOT NULL 
        AND CHAR_LENGTH(TRIM(content)) >= 5
        """
        
        # 添加时间过滤
        if start_time:
            start_timestamp = int(start_time.timestamp())
            base_sql += f" AND create_time >= {start_timestamp}"
        
        if end_time:
            end_timestamp = int(end_time.timestamp())
            base_sql += f" AND create_time <= {end_timestamp}"
        
        # 添加热门度过滤
        if min_likes > 0:
            base_sql += f" AND CAST(like_count AS UNSIGNED) >= {min_likes}"
        
        if min_sub_comments > 0:
            base_sql += f" AND CAST(sub_comment_count AS UNSIGNED) >= {min_sub_comments}"
        
        print(f"执行SQL查询: {base_sql}")
        
        # 读取数据
        df = pd.read_sql_query(base_sql, conn)
        print(f"原始数据量: {len(df)} 条")
        
        # 数据质量检查
        self.check_data_quality(df)
        
        # 过滤垃圾评论
        df_clean = self.filter_spam_comments(df)
        
        return df_clean
    
    def check_data_quality(self, df):
        """数据质量检查"""
        print("\n=== 数据质量检查 ===")
        print(f"空内容数量: {df['content'].isnull().sum()}")
        print(f"空评论ID数量: {df['comment_id'].isnull().sum()}")
        print(f"空视频ID数量: {df['aweme_id'].isnull().sum()}")
        print(f"空时间戳数量: {df['create_time'].isnull().sum()}")
    
    def filter_spam_comments(self, df):
        """过滤垃圾评论"""
        print("\n=== 过滤垃圾评论 ===")
        before_filter = len(df)
        
        df['is_spam'] = df.apply(
            lambda row: self.is_spam_comment(row['content'], row.get('user_signature')), 
            axis=1
        )
        
        df_clean = df[~df['is_spam']].copy()
        after_filter = len(df_clean)
        
        print(f"过滤前: {before_filter} 条")
        print(f"过滤后: {after_filter} 条")
        print(f"过滤掉: {before_filter - after_filter} 条垃圾评论")
        
        return df_clean
    
    def clean_and_process_data(self, df):
        """数据清洗和预处理"""
        print("\n=== 数据清洗阶段 ===")
        
        # 1. 时间格式转换
        print("1. 时间格式转换...")
        df['create_time_dt'] = pd.to_datetime(df['create_time'], unit='s')
        df['create_time_str'] = df['create_time_dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 2. 文本清洗
        print("2. 文本清洗...")
        df['content_cleaned'] = df['content'].apply(self.clean_text)
        
        # 3. 分词处理
        print("3. 分词处理...")
        df['content_segmented'] = df['content_cleaned'].apply(self.segment_text)
        df['word_count'] = df['content_segmented'].apply(len)
        
        # 4. 数据统计
        self.print_cleaning_stats(df)
        
        return df
    
    # 移除时间差计算函数，由时间分析模块负责
    
    def print_cleaning_stats(self, df):
        """打印清洗统计信息"""
        print("\n=== 清洗统计信息 ===")
        print(f"涉及视频数: {df['aweme_id'].nunique()}")
        print(f"涉及用户数: {df['user_id'].nunique()}")
        print(f"主评论数: {len(df[df['parent_comment_id'].isnull() | (df['parent_comment_id'] == '0')])}")
        print(f"子评论数: {len(df[df['parent_comment_id'].notnull() & (df['parent_comment_id'] != '0')])}")
        
        if not df.empty:
            min_time = df['create_time_dt'].min()
            max_time = df['create_time_dt'].max()
            print(f"时间范围: {min_time} 到 {max_time}")
        
        # 移除时间差统计，由时间分析模块负责
    
    def analyze_data_distribution(self, conn, start_time=None, end_time=None):
        """分析数据库中的数据分布"""
        print("\n" + "="*50)
        print("=== 数据库数据分布分析 ===")
        print("="*50)
        
        # 1. 总体数据统计
        print("\n📊 1. 总体数据统计")
        total_sql = "SELECT COUNT(*) as total FROM douyin_aweme_comment"
        total_count = pd.read_sql_query(total_sql, conn).iloc[0]['total']
        print(f"数据库总评论数: {total_count:,} 条")
        
        # 2. 时间分布分析
        print("\n📅 2. 时间分布分析")
        time_sql = """
        SELECT 
            DATE(FROM_UNIXTIME(create_time)) as date,
            COUNT(*) as count
        FROM douyin_aweme_comment
        WHERE create_time IS NOT NULL
        GROUP BY DATE(FROM_UNIXTIME(create_time))
        ORDER BY date DESC
        LIMIT 10
        """
        time_df = pd.read_sql_query(time_sql, conn)
        print("最近10天评论分布:")
        for _, row in time_df.iterrows():
            print(f"  {row['date']}: {row['count']:,} 条")
        
        # 3. 内容长度分布
        print("\n📏 3. 内容长度分布")
        length_sql = """
        SELECT 
            CASE 
                WHEN CHAR_LENGTH(content) < 10 THEN '0-9字符'
                WHEN CHAR_LENGTH(content) < 20 THEN '10-19字符'
                WHEN CHAR_LENGTH(content) < 50 THEN '20-49字符'
                WHEN CHAR_LENGTH(content) < 100 THEN '50-99字符'
                ELSE '100+字符'
            END as length_range,
            COUNT(*) as count
        FROM douyin_aweme_comment
        WHERE content IS NOT NULL
        GROUP BY length_range
        ORDER BY 
            CASE length_range
                WHEN '0-9字符' THEN 1
                WHEN '10-19字符' THEN 2
                WHEN '20-49字符' THEN 3
                WHEN '50-99字符' THEN 4
                ELSE 5
            END
        """
        length_df = pd.read_sql_query(length_sql, conn)
        print("内容长度分布:")
        for _, row in length_df.iterrows():
            percentage = (row['count'] / total_count) * 100
            print(f"  {row['length_range']}: {row['count']:,} 条 ({percentage:.1f}%)")
        
        # 4. 点赞数分布
        print("\n👍 4. 点赞数分布")
        likes_sql = """
        SELECT 
            CASE 
                WHEN CAST(like_count AS UNSIGNED) = 0 THEN '0点赞'
                WHEN CAST(like_count AS UNSIGNED) < 5 THEN '1-4点赞'
                WHEN CAST(like_count AS UNSIGNED) < 20 THEN '5-19点赞'
                WHEN CAST(like_count AS UNSIGNED) < 100 THEN '20-99点赞'
                ELSE '100+点赞'
            END as likes_range,
            COUNT(*) as count
        FROM douyin_aweme_comment
        WHERE like_count IS NOT NULL
        GROUP BY likes_range
        ORDER BY 
            CASE likes_range
                WHEN '0点赞' THEN 1
                WHEN '1-4点赞' THEN 2
                WHEN '5-19点赞' THEN 3
                WHEN '20-99点赞' THEN 4
                ELSE 5
            END
        """
        likes_df = pd.read_sql_query(likes_sql, conn)
        print("点赞数分布:")
        for _, row in likes_df.iterrows():
            percentage = (row['count'] / total_count) * 100
            print(f"  {row['likes_range']}: {row['count']:,} 条 ({percentage:.1f}%)")
        
        # 5. 子评论数分布
        print("\n💬 5. 子评论数分布")
        sub_comments_sql = """
        SELECT 
            CASE 
                WHEN CAST(sub_comment_count AS UNSIGNED) = 0 THEN '0子评论'
                WHEN CAST(sub_comment_count AS UNSIGNED) < 3 THEN '1-2子评论'
                WHEN CAST(sub_comment_count AS UNSIGNED) < 10 THEN '3-9子评论'
                WHEN CAST(sub_comment_count AS UNSIGNED) < 50 THEN '10-49子评论'
                ELSE '50+子评论'
            END as sub_comments_range,
            COUNT(*) as count
        FROM douyin_aweme_comment
        WHERE sub_comment_count IS NOT NULL
        GROUP BY sub_comments_range
        ORDER BY 
            CASE sub_comments_range
                WHEN '0子评论' THEN 1
                WHEN '1-2子评论' THEN 2
                WHEN '3-9子评论' THEN 3
                WHEN '10-49子评论' THEN 4
                ELSE 5
            END
        """
        sub_comments_df = pd.read_sql_query(sub_comments_sql, conn)
        print("子评论数分布:")
        for _, row in sub_comments_df.iterrows():
            percentage = (row['count'] / total_count) * 100
            print(f"  {row['sub_comments_range']}: {row['count']:,} 条 ({percentage:.1f}%)")
        
        # 6. 空内容统计
        print("\n❌ 6. 数据质量问题")
        null_content_sql = "SELECT COUNT(*) as null_count FROM douyin_aweme_comment WHERE content IS NULL OR content = ''"
        null_count = pd.read_sql_query(null_content_sql, conn).iloc[0]['null_count']
        null_percentage = (null_count / total_count) * 100
        print(f"空内容评论: {null_count:,} 条 ({null_percentage:.1f}%)")
        
        # 7. 热门视频统计
        print("\n🔥 7. 热门视频统计")
        hot_videos_sql = """
        SELECT 
            aweme_id,
            COUNT(*) as comment_count,
            AVG(CAST(like_count AS UNSIGNED)) as avg_likes,
            AVG(CAST(sub_comment_count AS UNSIGNED)) as avg_sub_comments
        FROM douyin_aweme_comment
        GROUP BY aweme_id
        HAVING comment_count >= 10
        ORDER BY comment_count DESC
        LIMIT 5
        """
        hot_videos_df = pd.read_sql_query(hot_videos_sql, conn)
        print("评论数最多的5个视频:")
        for _, row in hot_videos_df.iterrows():
            print(f"  视频ID {row['aweme_id']}: {row['comment_count']} 条评论, 平均点赞 {row['avg_likes']:.1f}, 平均子评论 {row['avg_sub_comments']:.1f}")
    
    def analyze_filtering_effect(self, conn, df_original, df_filtered):
        """分析过滤效果"""
        print("\n" + "="*50)
        print("=== 过滤效果分析 ===")
        print("="*50)
        
        # 获取数据库中的原始数据（未经过任何过滤）
        print("\n📊 获取原始数据库数据进行分析...")
        original_sql = """
        SELECT 
            comment_id, aweme_id, parent_comment_id, content, create_time, 
            like_count, sub_comment_count, user_id, nickname, user_signature
        FROM douyin_aweme_comment
        WHERE content IS NOT NULL
        """
        df_db_original = pd.read_sql_query(original_sql, conn)
        
        total_db_original = len(df_db_original)
        total_original = len(df_original)  # SQL过滤后的数据
        total_filtered = len(df_filtered)  # 垃圾评论过滤后的数据
        sql_filtered = total_db_original - total_original
        spam_filtered = total_original - total_filtered
        
        print(f"\n📊 总体过滤效果:")
        print(f"数据库原始数据: {total_db_original:,} 条")
        print(f"SQL过滤后数据: {total_original:,} 条")
        print(f"垃圾评论过滤后: {total_filtered:,} 条")
        print(f"SQL过滤掉: {sql_filtered:,} 条")
        print(f"垃圾评论过滤掉: {spam_filtered:,} 条")
        print(f"总过滤率: {((sql_filtered + spam_filtered) / total_db_original * 100):.2f}%")
        
        # 分析各过滤条件的效果（基于数据库原始数据）
        print(f"\n🔍 各过滤条件效果分析:")
        
        # 1. 内容长度过滤
        short_content = len(df_db_original[df_db_original['content'].str.len() < 5])
        short_percentage = (short_content / total_db_original) * 100
        print(f"1. 内容长度<5字符: {short_content:,} 条 ({short_percentage:.2f}%)")
        
        # 2. 特殊字符过滤
        special_char_filtered = 0
        for _, row in df_db_original.iterrows():
            content = row['content']
            if len(content) > 0:
                special_char_ratio = len(re.findall(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', content)) / len(content)
                if special_char_ratio > 0.6:
                    special_char_filtered += 1
        special_percentage = (special_char_filtered / total_db_original) * 100
        print(f"2. 特殊字符比例>60%: {special_char_filtered:,} 条 ({special_percentage:.2f}%)")
        
        # 3. 广告关键词过滤
        ad_keywords = [
            '加微信', '加qq', '加群', '私信', '联系我', '合作', '推广', '广告',
            '赚钱', '兼职', '代理', '加盟', '招商', '投资', '理财', '贷款',
            '免费领取', '限时优惠', '点击链接', '扫码关注', '关注公众号'
        ]
        ad_filtered = 0
        for _, row in df_db_original.iterrows():
            content_lower = row['content'].lower()
            for keyword in ad_keywords:
                if keyword in content_lower:
                    ad_filtered += 1
                    break
        ad_percentage = (ad_filtered / total_db_original) * 100
        print(f"3. 包含广告关键词: {ad_filtered:,} 条 ({ad_percentage:.2f}%)")
        
        # 4. 重复字符过滤
        repeated_filtered = 0
        for _, row in df_db_original.iterrows():
            content = row['content']
            if len(content) > 0 and len(set(content)) < len(content) * 0.2:
                repeated_filtered += 1
        repeated_percentage = (repeated_filtered / total_db_original) * 100
        print(f"4. 重复字符过多: {repeated_filtered:,} 条 ({repeated_percentage:.2f}%)")
        
        # 5. 用户签名过滤
        signature_filtered = 0
        for _, row in df_db_original.iterrows():
            user_signature = row.get('user_signature')
            if user_signature:
                if len(user_signature) > 100 or re.search(r'[0-9]{8,}', user_signature):
                    signature_filtered += 1
        signature_percentage = (signature_filtered / total_db_original) * 100
        print(f"5. 异常用户签名: {signature_filtered:,} 条 ({signature_percentage:.2f}%)")
        
        # 数据质量提升统计
        print(f"\n📈 数据质量提升:")
        if total_filtered > 0:
            # 计算过滤后的平均内容长度
            avg_length_original = df_db_original['content'].str.len().mean()
            avg_length_filtered = df_filtered['content'].str.len().mean()
            print(f"平均内容长度: {avg_length_original:.1f} → {avg_length_filtered:.1f} 字符")
            
            # 计算过滤后的特殊字符比例
            special_chars_original = 0
            special_chars_filtered = 0
            for _, row in df_db_original.iterrows():
                content = row['content']
                special_chars_original += len(re.findall(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', content))
            for _, row in df_filtered.iterrows():
                content = row['content']
                special_chars_filtered += len(re.findall(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', content))
            
            total_chars_original = df_db_original['content'].str.len().sum()
            total_chars_filtered = df_filtered['content'].str.len().sum()
            
            if total_chars_original > 0 and total_chars_filtered > 0:
                special_ratio_original = (special_chars_original / total_chars_original) * 100
                special_ratio_filtered = (special_chars_filtered / total_chars_filtered) * 100
                print(f"特殊字符比例: {special_ratio_original:.2f}% → {special_ratio_filtered:.2f}%")
    
    def save_processed_data(self, df, output_file):
        """保存处理后的数据"""
        print(f"\n=== 保存处理结果 ===")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 选择需要保存的字段
        save_columns = [
            'comment_id', 'aweme_id', 'parent_comment_id', 
            'content', 'content_cleaned', 'content_segmented',
            'create_time', 'create_time_dt', 'create_time_str',
            'like_count', 'sub_comment_count', 'word_count'
        ]
        
        df_save = df[save_columns].copy()
        
        # 保存为JSON
        df_save.to_json(output_file, orient='records', force_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {output_file}")
        print(f"📊 保存数据量: {len(df_save)} 条")
        
        # 显示数据预览
        print("\n=== 数据预览 ===")
        print(df_save.head(2).to_string())

def main():
    """主函数"""
    print("=== 抖音评论数据准备与清洗完整流程 ===")
    
    processor = CommentDataProcessor()
    
    try:
        # 获取数据库连接
        conn = get_db_conn()
        print("✅ 数据库连接成功")
        
        # 设置过滤条件
        # 选项1：最近90天数据
        # start_time = datetime.now() - timedelta(days=90)  # 最近90天
        # end_time = datetime.now()
        
        # 选项2：处理所有历史数据（取消注释下面的行）
        start_time = None  # 不限制开始时间
        end_time = None    # 不限制结束时间
        
        print(f"时间范围: {start_time} 到 {end_time}")
        
        # 第一阶段：数据准备（提取原始数据）
        print("\n" + "="*50)
        print("第一阶段：数据准备（提取原始数据）")
        print("="*50)
        
        df_raw = processor.get_raw_comments(
            conn=conn,
            start_time=start_time,
            end_time=end_time
        )
        
        if df_raw.empty:
            print("❌ 没有符合条件的数据")
            return
        
        # 第二阶段：数据过滤
        print("\n" + "="*50)
        print("第二阶段：数据过滤")
        print("="*50)
        
        df = processor.filter_spam_comments(df_raw)
        
        if df.empty:
            print("❌ 没有符合条件的数据")
            return
        
        # 第三阶段：数据清洗
        print("\n" + "="*50)
        print("第三阶段：数据清洗")
        print("="*50)
        
        df_processed = processor.clean_and_process_data(df)
        
        # 第四阶段：数据分布分析
        print("\n" + "="*50)
        print("第四阶段：数据分布分析")
        print("="*50)
        
        # 分析数据库中的数据分布
        processor.analyze_data_distribution(conn, start_time, end_time)
        
        # 分析过滤效果
        processor.analyze_filtering_effect(conn, df_raw, df_processed)
        
        # 保存结果
        output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'douyin_comments_processed.json')
        processor.save_processed_data(df_processed, output_file)
        
        print("\n✅ 数据准备、清洗与分析完成!")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    main() 