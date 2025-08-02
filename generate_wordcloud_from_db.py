import pymysql
import asyncio
import sys
import os

# 确保 tools/words.py 在导入路径下
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from tools.words import AsyncWordCloudGenerator

# 数据库连接配置（请根据你的 config/db_config.py 实际填写）
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PWD = 'root'
DB_NAME = 'media_crawler_db'

def fetch_comments():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM douyin_aweme_comment WHERE content IS NOT NULL")
    comments = [{'content': row[0]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return comments

async def main():
    comments = fetch_comments()
    if not comments:
        print("没有获取到评论内容，无法生成词云。")
        return
    generator = AsyncWordCloudGenerator()
    # 输出前缀，可自定义
    output_prefix = 'data/douyin/words/db_manual'
    await generator.generate_word_frequency_and_cloud(comments, output_prefix)
    print(f"词云图片和词频文件已生成在 {output_prefix}_word_cloud.png 和 {output_prefix}_word_freq.json")

if __name__ == "__main__":
    asyncio.run(main()) 