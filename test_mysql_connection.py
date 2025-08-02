import pymysql
from config.db_config import RELATION_DB_HOST, RELATION_DB_PORT, RELATION_DB_USER, RELATION_DB_PWD, RELATION_DB_NAME

try:
    connection = pymysql.connect(
        host=RELATION_DB_HOST,
        port=int(RELATION_DB_PORT),
        user=RELATION_DB_USER,
        password=RELATION_DB_PWD,
        database=RELATION_DB_NAME
    )
    print("MySQL连接成功！")
    connection.close()
except Exception as e:
    print("MySQL连接失败：", e) 