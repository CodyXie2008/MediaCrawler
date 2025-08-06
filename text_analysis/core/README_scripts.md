# 情感分析脚本使用说明

## 快速开始

### 1. 配置API密钥（仅阿里云API需要）

如果要使用阿里云API进行情感分析，需要先配置API密钥：

**方法一：环境变量**
```bash
# Windows PowerShell
$env:NLP_AK_ENV="your_access_key_id"
$env:NLP_SK_ENV="your_access_key_secret"
$env:NLP_REGION_ENV="cn-hangzhou"

# Windows CMD
set NLP_AK_ENV=your_access_key_id
set NLP_SK_ENV=your_access_key_secret
set NLP_REGION_ENV=cn-hangzhou

# Linux/macOS
export NLP_AK_ENV="your_access_key_id"
export NLP_SK_ENV="your_access_key_secret"
export NLP_REGION_ENV="cn-hangzhou"
```

**方法二：.env文件**
1. 复制 `env.example` 为 `.env`
2. 编辑 `.env` 文件，填入您的API密钥：
```
NLP_AK_ENV=your_access_key_id_here
NLP_SK_ENV=your_access_key_secret_here
NLP_REGION_ENV=cn-hangzhou
```

### 2. 运行脚本

**本地词典分析（推荐，无需网络）：**
```bash
cd text_analysis
python core/run_sentiment.py --type local
```

**阿里云API分析：**
```bash
cd text_analysis
python core/run_sentiment.py --type aliyun
```

**自动模式：**
```bash
cd text_analysis
python core/run_sentiment.py --type aliyun --auto
```

## 参数说明

- `--type`: 分析器类型
  - `local`: 本地词典分析（默认）
  - `aliyun`: 阿里云API分析
- `--auto`: 自动模式，跳过交互式选择界面

## 测试API连接

测试阿里云API是否配置正确：
```bash
cd text_analysis
python core/test_aliyun_connection.py
```

## 注意事项

1. **API密钥安全**：请勿将API密钥提交到Git仓库，`.env` 文件已被 `.gitignore` 忽略
2. **本地分析**：本地词典分析无需网络连接，推荐优先使用
3. **数据存储**：所有分析结果保存在项目根目录的 `data/` 文件夹中 