# 评论树可视化工具

一个独立的评论树可视化模块，用于展示评论的层级关系和互动情况。

## 📁 模块结构

```
comment_tree_visualizer/
├── __init__.py              # 模块初始化
├── main.py                  # 主程序入口
├── data_loader.py           # 数据加载器
├── tree_builder.py          # 评论树构建器
├── visualizer.py            # 可视化生成器
└── README.md               # 说明文档
```

## 🏗️ 评论树结构

### 数据结构说明

评论树采用层级结构表示，每个节点包含以下信息：

#### 节点属性
```json
{
  "id": "评论ID",
  "content": "评论内容",
  "create_time": 1640995200,
  "like_count": 15,
  "sub_comment_count": 3,
  "user_id": "用户ID",
  "nickname": "用户昵称",
  "depth": 0,
  "total_children": 0,
  "total_likes": 0,
  "children": []
}
```

#### 字段说明
- **id**: 评论唯一标识符
- **content**: 评论文本内容
- **create_time**: 评论创建时间（Unix时间戳）
- **like_count**: 该评论的点赞数
- **sub_comment_count**: 该评论的子评论数量
- **user_id**: 评论用户ID
- **nickname**: 用户昵称
- **depth**: 评论在树中的深度（0为根评论）
- **total_children**: 该节点下所有子评论总数
- **total_likes**: 该节点下所有评论的总点赞数
- **children**: 子评论数组

### 层级关系

```
虚拟根节点 (灰色)
├── 根评论1 (蓝色) - 直接回复视频
│   ├── 子评论1.1 (绿色) - 回复根评论1
│   │   └── 子评论1.1.1 (绿色) - 回复子评论1.1
│   └── 子评论1.2 (绿色) - 回复根评论1
├── 根评论2 (蓝色) - 直接回复视频
│   └── 子评论2.1 (绿色) - 回复根评论2
└── 根评论3 (红色) - 热门评论，点赞数>50
```

### 颜色编码

| 颜色 | 含义 | 条件 |
|------|------|------|
| 🔴 红色 | 热门评论 | 点赞数 > 50 |
| 🟡 黄色 | 高点赞评论 | 点赞数 > 20 |
| 🔵 蓝色 | 根评论 | 深度 = 0 |
| 🟢 绿色 | 子评论 | 深度 > 0 |
| ⚫ 灰色 | 虚拟根节点 | 系统生成 |

## 🚀 功能特性

### 核心功能
- ✅ **多数据源支持**: CSV、JSON、MySQL、SQLite、Processed数据
- ✅ **交互式可视化**: 基于D3.js的树形图展示
- ✅ **搜索功能**: 按评论内容或用户名搜索
- ✅ **节点展开/收起**: 点击节点控制显示
- ✅ **工具提示**: 鼠标悬停显示详细信息
- ✅ **统计信息**: 实时显示评论数据统计

### 可视化特性
- 🌳 **树形布局**: 清晰展示评论层级关系
- 🎨 **颜色区分**: 根据点赞数和深度区分节点类型
- 📏 **节点大小**: 支持按点赞数、回复数或固定大小显示
- 🔍 **搜索高亮**: 搜索结果快速定位
- 📱 **响应式设计**: 适配不同屏幕尺寸

## 📊 输出文件

生成的可视化文件包括：

1. **comment_tree_visualization.html** - 完整版交互式可视化
   - 基于D3.js的树形图
   - 支持搜索、展开/收起、工具提示
   - 实时统计信息显示

2. **comment_tree_simple.html** - 简化版可视化
   - 纯HTML/CSS/JavaScript实现
   - 不依赖外部库
   - 适合离线环境

3. **comment_tree_data.json** - 评论树数据
   - 完整的树形结构数据
   - 可用于其他分析工具

## 🛠️ 使用方法

### 命令行使用

```bash
# 从processed数据生成可视化
python main.py --source processed --output output_dir

# 从CSV文件生成可视化
python main.py --source csv --input data.csv --output output_dir

# 从JSON文件生成可视化
python main.py --source json --input data.json --output output_dir

# 从MySQL数据库生成可视化
python main.py --source mysql --db-name database --db-user user --db-password pass --output output_dir

# 自定义参数
python main.py --source processed --output output_dir --title "我的评论树" --max-depth 3
```

### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--source` | str | ✅ | - | 数据源类型 (csv/json/mysql/sqlite/processed) |
| `--input` | str | 条件 | - | 输入文件路径 (csv/json/sqlite模式必需) |
| `--output` | str | ❌ | output | 输出目录路径 |
| `--title` | str | ❌ | 评论树可视化 | 页面标题 |
| `--max-depth` | int | ❌ | 5 | 最大显示深度 |
| `--db-name` | str | 条件 | - | 数据库名称 (mysql模式必需) |
| `--db-user` | str | 条件 | - | 数据库用户名 (mysql模式必需) |
| `--db-password` | str | 条件 | - | 数据库密码 (mysql模式必需) |
| `--db-host` | str | ❌ | localhost | 数据库主机 |
| `--db-port` | int | ❌ | 3306 | 数据库端口 |

### 编程接口

```python
from data_loader import CommentDataLoader
from tree_builder import CommentTreeBuilder
from visualizer import CommentTreeVisualizer

# 加载数据
loader = CommentDataLoader()
df = loader.load_from_processed()

# 构建评论树
builder = CommentTreeBuilder()
tree_data = builder.build_tree(df, max_depth=5)

# 生成可视化
visualizer = CommentTreeVisualizer(tree_data)
visualizer.generate_html('output.html', '评论树可视化')
```

## 📋 数据源格式

### CSV格式
```csv
comment_id,parent_comment_id,content,create_time,like_count,sub_comment_count,user_id,nickname
1,0,这是一个很好的视频！,1640995200,15,3,user1,用户A
2,1,同意，内容很有价值,1640995260,8,1,user2,用户B
```

### JSON格式
```json
[
  {
    "comment_id": "1",
    "parent_comment_id": "0",
    "content": "这是一个很好的视频！",
    "create_time": 1640995200,
    "like_count": 15,
    "sub_comment_count": 3,
    "user_id": "user1",
    "nickname": "用户A"
  }
]
```

### 数据库表结构
```sql
CREATE TABLE comments (
    comment_id VARCHAR(50) PRIMARY KEY,
    parent_comment_id VARCHAR(50),
    content TEXT,
    create_time BIGINT,
    like_count INT,
    sub_comment_count INT,
    user_id VARCHAR(50),
    nickname VARCHAR(100)
);
```

## 🔧 技术实现

### 核心算法

1. **数据预处理**
   - 数据清洗和格式验证
   - 缺失值处理
   - 时间戳转换

2. **树形构建**
   - 基于parent_comment_id构建父子关系
   - 计算节点深度和统计信息
   - 生成虚拟根节点连接多个根评论

3. **可视化渲染**
   - D3.js树形布局算法
   - 节点颜色和大小映射
   - 交互事件处理

### 性能优化

- 支持大数据集的分页加载
- 树形结构的懒加载
- 搜索结果的缓存机制
- 响应式布局适配

## 📈 统计信息

生成的统计信息包括：

- **总评论数**: 所有评论的数量
- **根评论数**: 直接回复视频的评论数量
- **最大深度**: 评论树的最大层级深度
- **总点赞数**: 所有评论的点赞总数
- **平均点赞数**: 每条评论的平均点赞数

## 🎯 应用场景

- **社交媒体分析**: 分析评论互动模式
- **内容质量评估**: 通过评论热度评估内容质量
- **用户行为研究**: 研究用户评论习惯
- **社区管理**: 识别热门话题和争议内容
- **数据可视化**: 为报告和演示提供可视化支持

## 🔍 故障排除

### 常见问题

1. **数据加载失败**
   - 检查文件路径和格式
   - 验证数据库连接参数
   - 确认数据源权限

2. **可视化显示异常**
   - 检查浏览器兼容性
   - 确认D3.js库加载成功
   - 验证JSON数据格式

3. **性能问题**
   - 减少最大深度参数
   - 使用数据过滤条件
   - 考虑分页加载

## 📝 更新日志

### v1.0.0
- ✅ 初始版本发布
- ✅ 支持多种数据源
- ✅ 交互式树形可视化
- ✅ 搜索和过滤功能
- ✅ 响应式设计

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

---

**注意**: 本模块完全独立于主项目，可以单独使用和部署。
