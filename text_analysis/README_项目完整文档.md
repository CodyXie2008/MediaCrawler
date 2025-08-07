# MediaCrawler 文本分析项目完整文档

## 📋 目录

1. [项目概述](#项目概述)
2. [项目结构](#项目结构)
3. [核心功能](#核心功能)
4. [快速开始](#快速开始)
5. [详细使用指南](#详细使用指南)
6. [优化历程](#优化历程)
7. [技术架构](#技术架构)
8. [测试状态](#测试状态)
9. [未来规划](#未来规划)

## 🎯 项目概述

MediaCrawler 文本分析模块是一个专注于从众心理分析的综合性工具集，通过多维度分析（时间集中度、点赞互动、情感一致性、文本相似度）来识别和量化从众心理现象。

### 核心分析指标

| 指标 | 模块 | 说明 | 权重 |
|------|------|------|------|
| **时间集中度** | `time_analysis_optimized.py` | 评论时间分布集中程度 | 25% |
| **点赞集中度** | `like_analysis_optimized.py` | 点赞数分布集中程度 | 25% |
| **情感一致性** | `sentiment_analyzer_optimized.py` | 评论情感极性一致性 | 30% |
| **文本相似度** | 待开发 | 评论文本相似度 | 20% |

### 综合从众指数计算

```
从众指数 = 时间集中度 × 0.25 + 点赞集中度 × 0.25 + 情感一致性 × 0.30 + 文本相似度 × 0.20
```

## 🏗️ 项目结构

### 当前项目结构

```
text_analysis/
├── text_analysis_unified.py          # 🎯 统一入口工具（推荐使用）
├── core/                             # 核心基础设施
│   ├── data_paths.py                # 统一路径管理
│   ├── base_analyzer.py             # 基础分析器类
│   └── __init__.py
├── modules/                          # 分析模块（优化版）
│   ├── __init__.py
│   ├── data_cleaning_optimized.py         # 数据清洗模块
│   ├── sentiment_analyzer_optimized.py    # 情感分析模块
│   ├── time_analysis_optimized.py         # 时间分析模块
│   ├── like_analysis_optimized.py         # 点赞分析模块
│   ├── conformity_time_analysis.py        # 原始时间分析
│   ├── like_interaction_analysis.py       # 原始点赞分析
│   └── data_preparation_and_cleaning.py   # 原始数据清洗
├── docs/                             # 文档
│   ├── README.md                     # 项目概述
│   ├── 文本分析使用教程.md           # 详细使用教程（推荐）
│   ├── 情感分析算法文档.md           # 算法详解
│   ├── 从众心理时间分析功能算法文档.md
│   ├── 点赞互动分析算法文档.md
│   └── 数据清洗算法规则详解.md
├── env.example                       # 环境变量示例
└── README.md                         # 项目总览
```

### 数据存储结构

所有分析结果统一存储在`MediaCrawler/data/`目录：

```
MediaCrawler/data/
├── processed/                        # 清洗后的数据
│   └── cleaned_data_YYYYMMDD_HHMMSS.json
├── results/                          # 分析结果
│   ├── cleaning_analysis_YYYYMMDD_HHMMSS.csv
│   ├── sentiment_analysis_YYYYMMDD_HHMMSS.csv
│   ├── time_analysis_YYYYMMDD_HHMMSS.csv
│   └── like_analysis_YYYYMMDD_HHMMSS.csv
├── reports/                          # 分析报告
│   ├── cleaning_analysis_report_YYYYMMDD_HHMMSS.json
│   ├── sentiment_analysis_report_YYYYMMDD_HHMMSS.json
│   ├── time_analysis_report_YYYYMMDD_HHMMSS.json
│   └── like_analysis_report_YYYYMMDD_HHMMSS.json
└── visualizations/                   # 可视化图表
    ├── cleaning_analysis_main_YYYYMMDD_HHMMSS.png
    ├── sentiment_analysis_visualization_YYYYMMDD_HHMMSS.png
    ├── time_analysis_main_YYYYMMDD_HHMMSS.png
    └── like_analysis_main_YYYYMMDD_HHMMSS.png
```

## 🔧 核心功能

### 1. 数据清洗模块

**功能**：过滤垃圾评论，清洗文本数据，分词处理

**特性**：
- 数据质量检查（空内容、短内容、重复内容）
- 垃圾评论过滤
- 文本清洗和预处理
- 中文分词处理
- 数据质量评估

### 2. 情感分析模块

**功能**：分析评论情感极性，支持两种分析方式

**特性**：
- **本地词典分析**：无需网络，速度快，免费
- **阿里云API分析**：准确度高，支持复杂文本
- 批量情感分析
- 置信度评估
- 情感分布统计

### 3. 时间分析模块

**功能**：分析评论时间分布，识别从众心理时间窗口

**特性**：
- 时间差计算（父子评论时间间隔）
- 时间分布分析
- 密集时间段检测
- 从众窗口识别
- 时间集中度评估

### 4. 点赞分析模块

**功能**：分析点赞互动模式，识别意见领袖和社会认同信号

**特性**：
- 点赞分布统计
- 父评论点赞分析
- 意见领袖识别
- 社会认同信号检测
- 跟随速度分析

## 🚀 快速开始

### 环境准备

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp env.example .env
# 编辑.env文件，添加阿里云API密钥
```

### 统一入口使用（推荐）

```bash
# 查看帮助
python text_analysis_unified.py --help

# 测试所有模块
python text_analysis_unified.py cleaning --test
python text_analysis_unified.py sentiment --use-cleaned-data --type local --test
python text_analysis_unified.py time --use-cleaned-data --test
python text_analysis_unified.py like --use-cleaned-data --test
```

### 推荐分析流程

```bash
# 1. 数据清洗（必需）
python text_analysis_unified.py cleaning --video-id 123456

# 2. 时间分析（推荐）
python text_analysis_unified.py time --use-cleaned-data --video-id 123456

# 3. 点赞分析（推荐）
python text_analysis_unified.py like --use-cleaned-data --video-id 123456

# 4. 情感分析（推荐）
python text_analysis_unified.py sentiment --use-cleaned-data --type local --video-id 123456
```

## 📖 详细使用指南

### 通用参数说明

所有模块都支持以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--video-id` | str | None | 指定视频ID，不指定则分析所有数据 |
| `--limit` | int | None | 限制分析数量 |
| `--test` | flag | False | 测试模式，只分析10条数据 |
| `--use-cleaned-data` | flag | False | 使用清洗后的数据文件（推荐） |
| `--cleaned-data-path` | str | None | 指定清洗数据文件路径 |
| `--no-save` | flag | False | 不保存结果文件 |
| `--no-report` | flag | False | 不生成分析报告 |
| `--no-viz` | flag | False | 不创建可视化图表 |

### 1. 数据清洗模块

```bash
# 清洗所有数据
python text_analysis_unified.py cleaning

# 清洗指定视频的评论
python text_analysis_unified.py cleaning --video-id 123456

# 测试模式（只处理少量数据）
python text_analysis_unified.py cleaning --test

# 限制处理数量
python text_analysis_unified.py cleaning --limit 1000
```

### 2. 情感分析模块

```bash
# 使用本地词典分析（推荐用于测试）
python text_analysis_unified.py sentiment --use-cleaned-data --type local --test

# 使用阿里云API分析（推荐用于生产）
python text_analysis_unified.py sentiment --use-cleaned-data --type aliyun --test

# 分析指定视频的所有评论
python text_analysis_unified.py sentiment --use-cleaned-data --type local --video-id 123456

# 限制分析数量
python text_analysis_unified.py sentiment --use-cleaned-data --type local --limit 500
```

**分析器对比**：

| 特性 | 本地词典 | 阿里云API |
|------|----------|-----------|
| 准确度 | 中等 | 高 |
| 速度 | 快 | 中等 |
| 网络依赖 | 无 | 需要 |
| 成本 | 免费 | 按量计费 |
| 适用场景 | 测试、离线 | 生产环境 |

### 3. 时间分析模块

```bash
# 使用清洗数据进行分析
python text_analysis_unified.py time --use-cleaned-data --test

# 分析指定视频
python text_analysis_unified.py time --use-cleaned-data --video-id 123456

# 限制分析数量
python text_analysis_unified.py time --use-cleaned-data --limit 1000
```

### 4. 点赞分析模块

```bash
# 使用清洗数据进行分析
python text_analysis_unified.py like --use-cleaned-data --test

# 分析指定视频
python text_analysis_unified.py like --use-cleaned-data --video-id 123456

# 限制分析数量
python text_analysis_unified.py like --use-cleaned-data --limit 1000
```

## 🔄 优化历程

### 第一阶段：情感分析模块优化

**优化目标**：
1. API密钥隔离，避免上传到代码仓库
2. 代码结构优化，合并重复内容
3. 工作流程优化，支持视频ID分析
4. 参数化配置，支持命令行参数

**主要改进**：
- 环境变量配置（`.env`文件）
- 统一执行入口（`sentiment_analyzer_optimized.py`）
- 支持本地词典和阿里云API两种方式
- 完整的输出（CSV、JSON、报告、可视化）

### 第二阶段：项目结构统一优化

**优化目标**：
1. 统一项目结构，所有模块并列
2. 优化操作流程，支持指定视频ID和数据源
3. 优化文件命名，防止覆盖

**主要改进**：
- 创建`BaseAnalyzer`基类，提供统一接口
- 实现`AnalysisPathManager`，统一路径管理
- 支持时间戳和视频ID的文件命名
- 统一命令行参数解析

### 第三阶段：模块化架构优化

**优化目标**：
1. 将所有分析模块统一放置在`modules/`目录
2. 修复导入路径问题
3. 保持向后兼容性

**主要改进**：
- 模块统一管理，所有分析模块位于`modules/`目录
- 修复相对导入问题，使用绝对导入路径
- 保留原始模块，确保向后兼容
- 统一入口工具保持不变

## 🏛️ 技术架构

### 核心基础设施

#### BaseAnalyzer基类
- **功能**：为所有分析模块提供统一的基础功能
- **特性**：数据库连接、数据加载、结果保存、报告生成、可视化
- **方法**：
  - `_load_from_database()`: 从数据库加载数据
  - `_load_from_cleaned_data()`: 从清洗数据文件加载
  - `save_results()`: 保存分析结果
  - `generate_report()`: 生成分析报告
  - `create_visualizations()`: 创建可视化图表

#### AnalysisPathManager
- **功能**：统一管理所有输出路径
- **特性**：时间戳命名、视频ID支持、自动目录创建
- **方法**：
  - `get_cleaned_data_path()`: 获取清洗数据路径
  - `get_results_path()`: 获取结果文件路径
  - `get_report_path()`: 获取报告文件路径
  - `get_visualization_path()`: 获取可视化文件路径

### 数据流架构

```
原始数据 → 数据清洗 → 清洗数据 → 各分析模块 → 结果输出
    ↓           ↓           ↓           ↓           ↓
  数据库    垃圾过滤    预处理数据    分析处理    文件保存
    ↓           ↓           ↓           ↓           ↓
   MySQL    文本清洗     JSON文件    统计计算    CSV/JSON/PNG
```

### 模块依赖关系

```
text_analysis_unified.py (统一入口)
    ↓
BaseAnalyzer (基础功能)
    ↓
各分析模块 (具体实现)
    ↓
AnalysisPathManager (路径管理)
```

## 📈 测试状态

### 功能测试结果

| 模块 | 状态 | 测试数据量 | 备注 |
|------|------|------------|------|
| 数据清洗 | ✅ 通过 | 10条（测试模式） | 过滤率正常，输出完整 |
| 情感分析（本地） | ✅ 通过 | 10条（测试模式） | 分析准确，结果保存正常 |
| 情感分析（阿里云） | ✅ 通过 | 10条（测试模式） | API连接正常，精度较高 |
| 时间分析 | ✅ 通过 | 2001条（清洗数据） | 时间差计算正确 |
| 点赞分析 | ✅ 通过 | 2001条（清洗数据） | 点赞分布分析正常 |

### 数据存储验证

- ✅ 所有输出文件正确保存到`MediaCrawler/data/`
- ✅ 时间戳命名防止文件覆盖
- ✅ 分类存储便于管理
- ✅ 文件格式正确（CSV、JSON、PNG）

### 参数传递验证

- ✅ 统一入口工具参数传递正确
- ✅ 各模块参数解析正常
- ✅ 测试模式功能正常
- ✅ 视频ID指定功能正常

## 🚀 未来规划

### 短期目标

- [ ] 实现文本相似度分析模块
- [ ] 开发综合分析报告生成器
- [ ] 添加数据质量监控机制
- [ ] 优化算法性能和准确性

### 中期目标

- [ ] 增加批量处理功能
- [ ] 添加更多可视化图表类型
- [ ] 实现实时分析功能
- [ ] 开发Web界面

### 长期目标

- [ ] 支持更多数据源
- [ ] 实现分布式处理
- [ ] 开发API接口
- [ ] 集成机器学习模型

## 📚 相关文档

- **[📖 详细使用教程](docs/文本分析使用教程.md)** - 完整的使用指南和最佳实践
- **[🏗️ 项目结构总结](README_项目结构总结.md)** - 优化后的项目架构说明
- **[📋 项目概述](docs/README.md)** - 技术文档和算法详解

## 🔧 环境要求

- Python 3.7+
- 数据库连接（MySQL）
- 阿里云API（如果使用阿里云分析器）
- 依赖包：pandas、numpy、matplotlib、requests、jieba

## 📞 技术支持

如果在使用过程中遇到问题，请：

1. 查看[详细使用教程](docs/文本分析使用教程.md)
2. 检查控制台输出的错误信息
3. 确认环境配置是否正确
4. 查看各模块的详细算法文档

---

**最后更新**：2025-08-07  
**版本**：v2.0  
**状态**：✅ 功能完整，测试通过  
**作者**：CodyXie
