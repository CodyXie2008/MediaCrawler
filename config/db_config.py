# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


import os
import pymysql

# mysql config
RELATION_DB_PWD = os.getenv("RELATION_DB_PWD", "root")
RELATION_DB_USER = os.getenv("RELATION_DB_USER", "root")
RELATION_DB_HOST = os.getenv("RELATION_DB_HOST", "localhost")
RELATION_DB_PORT = int(os.getenv("RELATION_DB_PORT", 3306))
RELATION_DB_NAME = os.getenv("RELATION_DB_NAME", "media_crawler_db")


# redis config
REDIS_DB_HOST = "127.0.0.1"  # your redis host
REDIS_DB_PWD = os.getenv("REDIS_DB_PWD", "123456")  # your redis password
REDIS_DB_PORT = os.getenv("REDIS_DB_PORT", 6379)  # your redis port
REDIS_DB_NUM = os.getenv("REDIS_DB_NUM", 0)  # your redis db num

# cache type
CACHE_TYPE_REDIS = "redis"
CACHE_TYPE_MEMORY = "memory"

def get_db_conn():
    """
    获取MySQL数据库连接，自动读取本文件中的配置参数。
    用法：from config.db_config import get_db_conn; conn = get_db_conn()
    """
    return pymysql.connect(
        host=RELATION_DB_HOST,
        user=RELATION_DB_USER,
        password=RELATION_DB_PWD,
        port=RELATION_DB_PORT,
        database=RELATION_DB_NAME,
        charset='utf8mb4'
    )