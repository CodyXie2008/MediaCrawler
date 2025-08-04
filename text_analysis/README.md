# MediaCrawler 文本分析模块使用指南

## 📋 模块概述

MediaCrawler文本分析模块提供了强大的社交媒体数据分析功能，包括数据清洗、从众心理分析、点赞互动分析等。本模块基于爬虫收集的原始数据，通过科学的数据分析方法，挖掘用户行为模式和社交心理特征。

## 🗂️ 模块结构

```
text_analysis/
├── README.md                           # 本文档
├── data_preparation_and_cleaning.py    # 数据准备与清洗
├── like_interaction_analysis.py        # 点赞互动分析
├── conformity_time_analysis.py         # 从众心理时间分析
├── 数据清洗算法规则详解.md              # 数据清洗文档
├── 点赞互动分析算法文档.md              # 点赞分析文档
└── 从众心理时间分析功能算法文档.md      # 从众心理分析文档
```

## 🚀 快速开始

### 环境准备

1. **激活虚拟环境**（推荐）
```bash
# 在项目根目录
.\venv\Scripts\Activate.ps1
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **进入文本分析目录**
```bash
cd text_analysis
```

### 运行顺序

建议按以下顺序运行分析：

1. **数据准备与清洗** → 2. **点赞互动分析** → 3. **从众心理时间分析**

## 📊 功能模块详解

### 1. 数据准备与清洗 (`data_preparation_and_cleaning.py`)

**功能**：对原始爬虫数据进行清洗和预处理

**主要特性**：
- 垃圾评论过滤
- 文本标准化处理
- 数据质量检查
- 停用词处理
- 分词处理

**使用方法**：
```bash
python data_preparation_and_cleaning.py
```

**输出**：
- 清洗后的数据文件
- 数据质量报告
- 过滤效果统计

### 2. 点赞互动分析 (`like_interaction_analysis.py`)

**功能**：分析用户点赞行为和社会认同信号

**主要特性**：
- 点赞分布分析
- 意见领袖识别
- 社会认同信号分析
- 跟随速度计算
- 可视化图表生成

**使用方法**：
```bash
python like_interaction_analysis.py
```

**输出**：
- 点赞统计报告
- 意见领袖列表
- 社会认同分析结果
- 可视化图表

### 3. 从众心理时间分析 (`conformity_time_analysis.py`)

**功能**：分析用户从众心理的时间特征

**主要特性**：
- 时间序列分析
- 从众行为识别
- 群体效应分析
- 时间窗口统计
- 趋势分析

**使用方法**：
```bash
python conformity_time_analysis.py
```

**输出**：
- 时间序列分析报告
- 从众行为统计
- 群体效应分析结果
- 时间趋势图表

## ⚙️ 配置说明

### 数据库配置

确保 `config/db_config.py` 中的数据库连接配置正确：

```python
# 数据库连接参数
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "your_database"
```

### 分析参数配置

各分析模块支持自定义参数：

```python
# 点赞分析参数
like_threshold = 20          # 点赞阈值
follow_speed_threshold = 30  # 跟随速度阈值（分钟）

# 时间分析参数
time_window = 3600          # 时间窗口（秒）
conformity_threshold = 0.6   # 从众阈值
```

## 📈 输出结果说明

### 数据文件

- **清洗数据**：`../data/cleaned_comments.json`
- **分析结果**：`../data/analysis_results/`
- **可视化图表**：`../data/visualizations/`
- **分析报告**：`../data/reports/`

### 报告内容

1. **数据质量报告**
   - 原始数据统计
   - 清洗效果统计
   - 数据分布分析

2. **点赞互动报告**
   - 点赞分布统计
   - 意见领袖列表
   - 社会认同信号分析

3. **从众心理报告**
   - 时间序列分析
   - 从众行为统计
   - 群体效应分析

## 🔧 高级用法

### 自定义分析参数

```python
# 修改分析参数
analyzer = LikeInteractionAnalyzer()
analyzer.like_thresholds = {
    'low': 0,
    'medium': 10,      # 自定义中等点赞阈值
    'high': 50,        # 自定义高点赞阈值
    'very_high': 200,  # 自定义很高点赞阈值
    'viral': 1000      # 自定义病毒级阈值
}
```

### 批量处理

```python
# 批量处理多个时间范围
time_ranges = [
    ('2024-01-01', '2024-01-31'),
    ('2024-02-01', '2024-02-29'),
    ('2024-03-01', '2024-03-31')
]

for start_date, end_date in time_ranges:
    # 执行分析
    pass
```

## 🐛 常见问题

### 1. 数据库连接失败

**问题**：`ModuleNotFoundError: No module named 'config'`

**解决**：确保在正确的目录下运行，或添加路径：
```python
import sys
sys.path.append('..')
```

### 2. 依赖包缺失

**问题**：`ModuleNotFoundError: No module named 'numpy'`

**解决**：安装缺失的依赖：
```bash
pip install numpy pandas matplotlib jieba
```

### 3. 数据文件不存在

**问题**：`FileNotFoundError: No such file or directory`

**解决**：确保先运行爬虫收集数据，或检查文件路径

### 4. 内存不足

**问题**：处理大量数据时内存不足

**解决**：
- 分批处理数据
- 增加系统内存
- 使用数据采样

## 📝 使用建议

1. **数据准备**：确保爬虫数据完整且格式正确
2. **参数调优**：根据具体场景调整分析参数
3. **结果验证**：结合业务场景验证分析结果
4. **定期更新**：定期更新分析模型和参数

## 🔗 相关文档

- [数据清洗算法规则详解](./数据清洗算法规则详解.md)
- [点赞互动分析算法文档](./点赞互动分析算法文档.md)
- [从众心理时间分析功能算法文档](./从众心理时间分析功能算法文档.md)
- [主项目README](../README.md)

## 📞 技术支持

如遇到问题，请参考：
1. 本文档的常见问题部分
2. 各模块的详细算法文档
3. 项目主文档和配置说明 