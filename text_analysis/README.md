# MediaCrawler 文本分析模块

## 📋 项目概述

MediaCrawler 文本分析模块是一个专注于从众心理分析的综合性工具集，通过多维度分析（时间集中度、点赞互动、情感一致性、文本相似度）来识别和量化从众心理现象。

## 🚀 快速开始

### 情感分析
```bash
# 本地词典分析（默认）
python core/run_sentiment.py --type local

# 阿里云API分析
python core/run_sentiment.py --type aliyun
```

### 时间分析
```bash
python modules/conformity_time_analysis.py
```

### 数据清洗
```bash
python modules/data_preparation_and_cleaning.py
```

## 🎯 核心分析指标

| 指标 | 模块 | 说明 | 权重 |
|------|------|------|------|
| **时间集中度** | `conformity_time_analysis.py` | 评论时间分布集中程度 | 25% |
| **点赞集中度** | `like_interaction_analysis.py` | 点赞数分布集中程度 | 25% |
| **情感一致性** | `sentiment_analysis_simple.py` | 评论情感极性一致性 | 30% |
| **文本相似度** | 待开发 | 评论文本相似度 | 20% |

## 📁 项目结构

```
text_analysis/
├── core/                           # 核心模块
│   ├── run_sentiment.py           # 统一情感分析脚本
│   ├── sentiment_analysis_simple.py # 情感分析核心模块
│   ├── data_paths.py              # 路径管理配置
│   └── README_scripts.md          # 脚本使用说明
│
├── modules/                        # 分析模块
│   ├── conformity_time_analysis.py     # 时间集中度分析
│   ├── like_interaction_analysis.py    # 点赞互动分析
│   └── data_preparation_and_cleaning.py # 数据清洗模块
│
├── data/                          # 数据存储
│   ├── raw/                       # 原始数据
│   ├── processed/                 # 处理后数据
│   ├── results/                   # 分析结果
│   ├── reports/                   # 分析报告
│   └── visualizations/            # 可视化图表
│
└── docs/                          # 详细文档
    ├── README.md                  # 完整使用指南
    ├── 情感分析算法文档.md        # 情感分析算法详解
    ├── 从众心理时间分析功能算法文档.md # 时间分析算法
    ├── 点赞互动分析算法文档.md    # 点赞分析算法
    └── 数据清洗算法规则详解.md    # 数据清洗规则
```

## 📚 详细文档

- **[完整使用指南](docs/README.md)** - 详细的项目说明和使用方法
- [情感分析算法文档](docs/情感分析算法文档.md) - 情感分析算法详解
- [从众心理时间分析功能算法文档](docs/从众心理时间分析功能算法文档.md) - 时间分析算法
- [点赞互动分析算法文档](docs/点赞互动分析算法文档.md) - 点赞分析算法
- [数据清洗算法规则详解](docs/数据清洗算法规则详解.md) - 数据清洗规则

## 🔧 环境要求

- Python 3.7+
- 数据库连接（MySQL）
- 阿里云API（如果使用阿里云分析器）
- 依赖包：pandas、numpy、matplotlib、requests

## 📈 测试状态

- ✅ 情感分析模块：通过
- ✅ 时间分析模块：通过
- ✅ 数据清洗模块：通过
- ⚠️ 点赞分析模块：部分通过（数据格式问题待修复）

## 🚀 未来规划

- [ ] 修复点赞分析模块数据格式问题
- [ ] 实现文本相似度分析模块
- [ ] 开发综合分析报告生成器
- [ ] 添加数据质量监控机制 