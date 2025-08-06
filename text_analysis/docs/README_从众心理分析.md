# 从众心理情感分析模块使用指南

## 🎯 功能概述

本模块在原有情感分析基础上，增加了从众心理分析功能，可以分析社交媒体评论中的从众行为模式。

### 主要功能

1. **情感分析**：分析评论的情感倾向（正向、负向、中性）
2. **从众时间分析**：计算评论与父评论的时间差，识别从众时间窗口
3. **情感从众分析**：分析情感一致性，识别情感从众行为
4. **综合从众指标**：计算从众强度指数，标记高从众评论

## 🚀 快速开始

### 1. 基础使用

```python
from sentiment_analysis import SentimentAnalysisManager

# 创建分析器
manager = SentimentAnalysisManager("dictionary")

# 连接数据库
conn = get_db_conn()

# 进行从众心理分析
df = manager.analyze_conformity_sentiment(
    conn=conn,
    aweme_id=None,  # 可指定特定视频ID
    start_time='2024-01-01',
    end_time='2024-01-31',
    limit=1000
)

# 保存结果
manager.save_conformity_results(df, "conformity_results.csv")
manager.generate_conformity_report(df, "conformity_report.json")
```

### 2. 运行示例脚本

```bash
cd text_analysis
python conformity_sentiment_example.py
```

## 📊 分析字段说明

### 新增字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `time_diff_minutes` | float | 与父评论的时间差（分钟） |
| `conformity_window` | string | 从众时间窗口分类 |
| `conformity_strength` | float | 从众强度（0-1） |
| `sentiment_conformity` | float | 情感从众度（-1到1） |
| `conformity_index` | float | 综合从众指数（0-1） |
| `is_high_conformity` | bool | 是否高从众评论 |

### 从众时间窗口分类

| 窗口类型 | 时间范围 | 说明 |
|----------|----------|------|
| `independent` | - | 独立评论（无父评论） |
| `immediate` | 0-5分钟 | 立即从众 |
| `quick` | 5-30分钟 | 快速从众 |
| `medium` | 30分钟-2小时 | 中等从众 |
| `slow` | 2小时-1天 | 缓慢从众 |
| `delayed` | 1天-1周 | 延迟从众 |
| `long_term` | 1周以上 | 长期从众 |

## 🔧 高级使用

### 1. 自定义分析参数

```python
# 指定视频ID进行分析
df = manager.analyze_conformity_sentiment(
    conn=conn,
    aweme_id="your_video_id",
    start_time=start_time,
    end_time=end_time,
    limit=1000
)

# 只分析主评论（不包含回复）
df = manager.analyze_comments_from_db(
    conn=conn,
    include_replies=False,
    include_sentiment=True
)
```

### 2. 分析特定时间窗口

```python
# 筛选特定从众窗口的评论
immediate_conformity = df[df['conformity_window'] == 'immediate']
high_conformity = df[df['is_high_conformity'] == True]

print(f"立即从众评论数: {len(immediate_conformity)}")
print(f"高从众评论数: {len(high_conformity)}")
```

### 3. 情感从众分析

```python
# 分析不同情感类型的从众行为
for sentiment in ['positive', 'negative', 'neutral']:
    sentiment_df = df[df['sentiment'] == sentiment]
    avg_conformity = sentiment_df['sentiment_conformity'].mean()
    print(f"{sentiment}评论平均从众度: {avg_conformity:.3f}")
```

## 📈 结果解读

### 从众指数计算

综合从众指数 = 时间强度 × 0.6 + 情感一致性 × 0.4

- **时间强度**：基于与父评论的时间差计算
- **情感一致性**：与父评论的情感匹配程度

### 高从众评论识别

- 从众指数 > 0.7 的评论被标记为高从众评论
- 这些评论通常表现出强烈的从众行为特征

### 情感从众度

- **1.0**：与父评论情感完全一致
- **0.0**：与父评论情感无关（中性）
- **-1.0**：与父评论情感对立

## 📁 输出文件

### 1. CSV结果文件

包含所有分析字段的详细数据：
- 评论基本信息
- 情感分析结果
- 从众分析指标

### 2. JSON报告文件

包含统计摘要：
- 从众窗口分布
- 情感从众统计
- 高从众评论比例
- 从众指数统计

## 🎨 实际应用示例

### 示例1：分析热门视频的从众行为

```python
def analyze_hot_video_conformity(video_id):
    """分析热门视频的从众行为"""
    manager = SentimentAnalysisManager("dictionary")
    conn = get_db_conn()
    
    # 分析最近24小时的评论
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    df = manager.analyze_conformity_sentiment(
        conn=conn,
        aweme_id=video_id,
        start_time=start_time,
        end_time=end_time
    )
    
    # 分析立即从众行为
    immediate = df[df['conformity_window'] == 'immediate']
    print(f"立即从众评论: {len(immediate)} ({len(immediate)/len(df):.2%})")
    
    # 分析情感从众
    positive_conformity = df[df['sentiment'] == 'positive']['sentiment_conformity'].mean()
    print(f"正向评论从众度: {positive_conformity:.3f}")
```

### 示例2：比较不同平台的从众行为

```python
def compare_platform_conformity():
    """比较不同平台的从众行为"""
    manager = SentimentAnalysisManager("dictionary")
    conn = get_db_conn()
    
    platforms = ['douyin', 'kuaishou', 'bilibili']
    
    for platform in platforms:
        df = manager.analyze_conformity_sentiment(
            conn=conn,
            platform=platform,
            limit=500
        )
        
        avg_conformity = df['conformity_index'].mean()
        high_conformity_ratio = df['is_high_conformity'].mean()
        
        print(f"{platform}:")
        print(f"  平均从众指数: {avg_conformity:.3f}")
        print(f"  高从众比例: {high_conformity_ratio:.2%}")
```

## ⚠️ 注意事项

1. **数据库字段要求**：确保数据库中有 `parent_comment_id` 和 `created_time` 字段
2. **时间格式**：确保时间字段格式正确
3. **性能考虑**：大量数据时建议分批处理
4. **内存使用**：从众分析会加载所有相关评论到内存

## 🔍 故障排除

### 1. 数据为空

```python
# 检查数据库连接和数据
if df.empty:
    print("检查数据库连接和查询条件")
    # 尝试基础查询
    basic_df = manager.analyze_comments_from_db(conn, limit=10)
    print(f"基础查询结果: {len(basic_df)} 条")
```

### 2. 字段缺失

```python
# 检查必要字段
required_fields = ['parent_comment_id', 'created_time', 'content']
missing_fields = [field for field in required_fields if field not in df.columns]
if missing_fields:
    print(f"缺少字段: {missing_fields}")
```

### 3. 时间计算错误

```python
# 检查时间字段格式
print(f"时间字段类型: {df['created_time'].dtype}")
print(f"时间范围: {df['created_time'].min()} 到 {df['created_time'].max()}")
```

## 📞 技术支持

如果遇到问题，请参考：
1. `conformity_sentiment_example.py` - 完整使用示例
2. `sentiment_analysis.py` - 核心代码实现
3. 数据库连接配置文档
4. 项目README文档 