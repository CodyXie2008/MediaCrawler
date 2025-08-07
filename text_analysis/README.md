# MediaCrawler 文本分析模块

## 📋 项目概述

MediaCrawler 文本分析模块是一个专注于从众心理分析的综合性工具集，通过多维度分析（时间集中度、点赞互动、情感一致性、文本相似度）来识别和量化从众心理现象。

## 📚 文档导航

- **[📖 项目完整文档](README_项目完整文档.md)** - 完整的项目文档，包含概述、结构、功能、使用指南等（推荐）
- **[📖 详细使用教程](docs/文本分析使用教程.md)** - 详细的使用指南和最佳实践
- **[📋 项目概述](docs/README.md)** - 技术文档和算法详解

## 🚀 快速开始

### 统一入口使用（推荐）
```bash
# 情感分析
python text_analysis_unified.py sentiment --test
python text_analysis_unified.py sentiment --video-id 123456 --type aliyun

# 时间分析
python text_analysis_unified.py time --test
python text_analysis_unified.py time --video-id 123456 --limit 1000

# 点赞分析
python text_analysis_unified.py like --test
python text_analysis_unified.py like --video-id 123456 --use-cleaned-data

# 数据清洗
python text_analysis_unified.py cleaning --test
python text_analysis_unified.py cleaning --video-id 123456 --limit 5000
```

### 直接模块使用
```bash
# 情感分析
python -m text_analysis.modules.sentiment_analyzer_optimized --test

# 时间分析
python -m text_analysis.modules.time_analysis_optimized --test

# 点赞分析
python -m text_analysis.modules.like_analysis_optimized --test

# 数据清洗
python -m text_analysis.modules.data_cleaning_optimized --test
```

## 🎯 核心分析指标

| 指标 | 模块 | 说明 | 权重 |
|------|------|------|------|
| **时间集中度** | `time_analysis_optimized.py` | 评论时间分布集中程度 | 25% |
| **点赞集中度** | `like_analysis_optimized.py` | 点赞数分布集中程度 | 25% |
| **情感一致性** | `sentiment_analyzer_optimized.py` | 评论情感极性一致性 | 30% |
| **文本相似度** | 待开发 | 评论文本相似度 | 20% |

## 📁 项目结构

```
text_analysis/
├── text_analysis_unified.py           # 统一入口（推荐使用）
├── modules/                           # 所有分析模块
│   ├── __init__.py                    # 模块导入管理
│   ├── sentiment_analyzer_optimized.py    # 优化版情感分析
│   ├── time_analysis_optimized.py         # 优化版时间分析
│   ├── like_analysis_optimized.py         # 优化版点赞分析
│   ├── data_cleaning_optimized.py         # 优化版数据清洗
│   ├── conformity_time_analysis.py        # 旧版时间分析（向后兼容）
│   ├── like_interaction_analysis.py       # 旧版点赞分析（向后兼容）
│   └── data_preparation_and_cleaning.py   # 旧版数据清洗（向后兼容）
│
├── core/                              # 核心功能
│   ├── base_analyzer.py               # 基础分析器类
│   ├── data_paths.py                  # 路径管理
│   └── __init__.py
│
├── data/                              # 数据存储
│   ├── raw/                           # 原始数据
│   ├── processed/                     # 处理后数据
│   ├── results/                       # 分析结果
│   ├── reports/                       # 分析报告
│   └── visualizations/                # 可视化图表
│
└── docs/                              # 详细文档
    ├── README.md                      # 完整使用指南
    ├── 情感分析算法文档.md            # 情感分析算法详解
    ├── 从众心理时间分析功能算法文档.md # 时间分析算法
    ├── 点赞互动分析算法文档.md        # 点赞分析算法
    └── 数据清洗算法规则详解.md        # 数据清洗规则
```

## 📚 详细文档

- **[完整使用指南](docs/README.md)** - 详细的项目说明和使用方法
- **[项目结构优化总结](README_项目结构优化.md)** - 最新的项目结构优化说明
- **[优化总结](README_优化总结.md)** - 整体优化过程总结
- [情感分析算法文档](docs/情感分析算法文档.md) - 情感分析算法详解
- [从众心理时间分析功能算法文档](docs/从众心理时间分析功能算法文档.md) - 时间分析算法
- [点赞互动分析算法文档](docs/点赞互动分析算法文档.md) - 点赞分析算法
- [数据清洗算法规则详解](docs/数据清洗算法规则详解.md) - 数据清洗规则

## 🔧 环境要求

- Python 3.7+
- 数据库连接（MySQL）
- 阿里云API（如果使用阿里云分析器）
- 依赖包：pandas、numpy、matplotlib、requests、jieba

## 📈 测试状态

- ✅ 情感分析模块：通过（支持本地词典和阿里云API）
- ✅ 时间分析模块：通过（从众心理时间分析）
- ✅ 点赞分析模块：通过（点赞互动分析）
- ✅ 数据清洗模块：通过（数据预处理和清洗）

## 🆕 最新优化

### 项目结构优化
- **模块统一管理**：所有分析模块统一放置在 `modules/` 目录
- **向后兼容**：保留旧版本模块，确保现有代码不受影响
- **导入优化**：修复相对导入问题，使用绝对导入路径
- **统一入口**：`text_analysis_unified.py` 提供统一的使用接口

### 功能增强
- **BaseAnalyzer基类**：为所有分析模块提供统一的基础功能
- **路径管理优化**：支持带时间戳和视频ID的文件命名，防止覆盖
- **参数化配置**：支持指定视频ID、数据源、分析类型等
- **测试模式**：提供 `--test` 参数进行快速测试

## 🚀 未来规划

- [ ] 实现文本相似度分析模块
- [ ] 开发综合分析报告生成器
- [ ] 添加数据质量监控机制
- [ ] 优化算法性能和准确性
- [ ] 添加更多可视化图表类型 