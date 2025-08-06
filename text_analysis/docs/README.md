# MediaCrawler 文本分析模块

## 📋 项目概述

MediaCrawler 文本分析模块是一个专注于从众心理分析的综合性工具集，通过多维度分析（时间集中度、点赞互动、情感一致性、文本相似度）来识别和量化从众心理现象。

## 🏗️ 项目结构

```
text_analysis/
├── core/                           # 核心模块
│   ├── run_sentiment.py           # 统一情感分析脚本
│   ├── sentiment_analysis_simple.py # 情感分析核心模块
│   ├── data_paths.py              # 路径管理配置
│   ├── test_aliyun_connection.py  # 阿里云API连接测试
│   └── README_scripts.md          # 脚本使用说明
│
├── modules/                        # 分析模块
│   ├── conformity_time_analysis.py     # 时间集中度分析
│   ├── like_interaction_analysis.py    # 点赞互动分析
│   ├── data_preparation_and_cleaning.py # 数据清洗模块
│   └── __init__.py
│
├── data/                          # 数据存储
│   ├── raw/                       # 原始数据
│   ├── processed/                 # 处理后数据
│   ├── results/                   # 分析结果
│   ├── reports/                   # 分析报告
│   ├── visualizations/            # 可视化图表
│   └── temp/                      # 临时文件
│
├── docs/                          # 文档
│   ├── README.md                  # 本文档
│   ├── 情感分析算法文档.md        # 情感分析算法详解
│   ├── 从众心理时间分析功能算法文档.md # 时间分析算法
│   ├── 点赞互动分析算法文档.md    # 点赞分析算法
│   ├── 数据清洗算法规则详解.md    # 数据清洗规则
│   └── hit_stopwords.txt          # 停用词表
│
└── README.md                      # 项目总览
```

## 🎯 核心分析指标

从众心理分析基于四个核心指标构建综合评估体系：

| 指标 | 模块 | 说明 | 权重 |
|------|------|------|------|
| **时间集中度** | `conformity_time_analysis.py` | 评论时间分布集中程度 | 25% |
| **点赞集中度** | `like_interaction_analysis.py` | 点赞数分布集中程度 | 25% |
| **情感一致性** | `sentiment_analysis_simple.py` | 评论情感极性一致性 | 30% |
| **文本相似度** | 待开发 | 评论文本相似度 | 20% |

### 综合从众指数计算

```
从众指数 = 时间集中度 × 0.25 + 点赞集中度 × 0.25 + 情感一致性 × 0.30 + 文本相似度 × 0.20
```

## 🚀 快速开始

### 1. 情感分析

#### 统一情感分析脚本
```bash
# 查看帮助
python core/run_sentiment.py --help

# 本地词典分析（默认）
python core/run_sentiment.py --type local

# 阿里云API分析
python core/run_sentiment.py --type aliyun

# 自动模式
python core/run_sentiment.py --type local --auto
```

#### 功能对比

| 分析器类型 | 优点 | 缺点 | 适用场景 |
|-----------|------|------|----------|
| 本地词典 | 无需网络、速度快、免费 | 准确度相对较低 | 离线环境、快速测试 |
| 阿里云API | 准确度高、支持复杂文本 | 需要网络、有API限制 | 生产环境、高精度需求 |

### 2. 时间分析
```bash
python modules/conformity_time_analysis.py
```

### 3. 数据清洗
```bash
python modules/data_preparation_and_cleaning.py
```

## 📊 模块功能详解

### 🔧 核心模块

#### `core/run_sentiment.py` - 统一情感分析脚本
- **功能**: 支持本地词典和阿里云API两种分析方式
- **参数**: 
  - `--type {local,aliyun}`: 选择分析器类型
  - `--auto`: 自动模式，跳过交互式选择
- **输出**: 结果文件、报告、可视化图表

#### `core/sentiment_analysis_simple.py` - 情感分析核心模块
- **支持**: 阿里云NLP API、本地词典分析
- **功能**: 批量情感分析、结果保存、报告生成、可视化
- **核心类**: `DictionaryAnalyzer`、`AliyunAnalyzer`、`SentimentManager`

#### `core/data_paths.py` - 路径管理配置
- **功能**: 统一管理所有数据存储路径
- **特性**: 自动目录创建、时间戳文件名、模块化路径管理
- **核心类**: `PathManager`

### 📊 分析模块

#### `modules/conformity_time_analysis.py` - 时间集中度分析
- **功能**: 分析评论时间分布，检测从众行为时间窗口
- **指标**: 时间差统计、时间窗口分布、密集时间段检测
- **输出**: 时间分析报告、可视化图表

#### `modules/like_interaction_analysis.py` - 点赞互动分析
- **功能**: 分析点赞数分布，识别点赞集中现象
- **指标**: 点赞分布统计、点赞集中度计算
- **输出**: 点赞分析报告、可视化图表

#### `modules/data_preparation_and_cleaning.py` - 数据清洗模块
- **功能**: 数据质量检查、垃圾评论过滤、文本清洗
- **处理**: 分词处理、数据分布分析、质量评估
- **输出**: 清洗后数据、清洗报告

## 📁 数据存储结构

```
data/
├── raw/           # 原始数据
├── processed/     # 处理后数据
├── results/       # 分析结果
├── reports/       # 分析报告
├── visualizations/ # 可视化图表
└── temp/          # 临时文件
```

### 文件命名规范
- 时间戳格式: `YYYYMMDD_HHMMSS`
- 模块标识: `sentiment_analysis_`、`time_analysis_`、`like_analysis_`
- 文件类型: `.csv`、`.json`、`.png`

## 🔧 环境要求

- Python 3.7+
- 数据库连接（MySQL）
- 阿里云API（如果使用阿里云分析器）
- 依赖包：pandas、numpy、matplotlib、requests

## 📚 详细文档

- [情感分析算法文档](docs/情感分析算法文档.md) - 情感分析算法详解
- [从众心理时间分析功能算法文档](docs/从众心理时间分析功能算法文档.md) - 时间分析算法
- [点赞互动分析算法文档](docs/点赞互动分析算法文档.md) - 点赞分析算法
- [数据清洗算法规则详解](docs/数据清洗算法规则详解.md) - 数据清洗规则

## 🎯 从众心理分析应用

### 情感一致性指标
```
情感一致性 = 1 - 情感分布熵值
```

### 从众心理识别
1. **情感从众**: 大量评论表达相同情感
2. **情感极化**: 评论情感呈现两极分化
3. **情感传染**: 情感在评论间传播扩散
4. **时间从众**: 评论时间高度集中
5. **点赞从众**: 点赞数分布异常集中

## 📈 测试结果

最新测试结果显示：
- ✅ 情感分析模块：通过（50条评论测试）
- ✅ 时间分析模块：通过（2008条有效数据）
- ✅ 数据清洗模块：通过（2758→2185条，过滤率20.78%）
- ⚠️ 点赞分析模块：部分通过（数据格式问题待修复）

## 🚀 未来规划

- [ ] 修复点赞分析模块数据格式问题
- [ ] 实现文本相似度分析模块
- [ ] 开发综合分析报告生成器
- [ ] 添加数据质量监控机制
- [ ] 优化可视化图表样式
- [ ] 增加批量处理功能 