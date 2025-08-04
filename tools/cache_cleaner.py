# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Name    : 程序员阿江-Relakkes
# @Time    : 2024/12/19
# @Desc    : 缓存清理工具

import os
import shutil
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cache.cache_factory import CacheFactory
from config import db_config
from tools import utils


class CacheCleaner:
    """缓存清理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.browser_data_dir = self.project_root / "browser_data"
        
    def clean_memory_cache(self):
        """清理内存缓存"""
        try:
            utils.logger.info("开始清理内存缓存...")
            
            # 创建内存缓存实例
            memory_cache = CacheFactory.create_cache('memory')
            
            # 获取所有缓存键
            all_keys = memory_cache.keys('*')
            
            if all_keys:
                utils.logger.info(f"发现 {len(all_keys)} 个内存缓存项")
                for key in all_keys:
                    utils.logger.info(f"  - 清理缓存键: {key}")
                # 内存缓存会自动过期，这里主要是记录日志
            else:
                utils.logger.info("内存缓存为空，无需清理")
                
            utils.logger.info("内存缓存清理完成")
            return True
            
        except Exception as e:
            utils.logger.error(f"清理内存缓存失败: {e}")
            return False
    
    def clean_redis_cache(self):
        """清理Redis缓存"""
        try:
            utils.logger.info("开始清理Redis缓存...")
            
            # 创建Redis缓存实例
            redis_cache = CacheFactory.create_cache('redis')
            
            # 获取所有缓存键
            all_keys = redis_cache.keys('*')
            
            if all_keys:
                utils.logger.info(f"发现 {len(all_keys)} 个Redis缓存项")
                
                # 清理所有键
                for key in all_keys:
                    utils.logger.info(f"  - 清理缓存键: {key}")
                    redis_cache._redis_client.delete(key)
                    
                utils.logger.info("Redis缓存清理完成")
            else:
                utils.logger.info("Redis缓存为空，无需清理")
                
            return True
            
        except Exception as e:
            utils.logger.error(f"清理Redis缓存失败: {e}")
            return False
    
    def clean_browser_cache(self):
        """清理浏览器缓存"""
        try:
            utils.logger.info("开始清理浏览器缓存...")
            
            if not self.browser_data_dir.exists():
                utils.logger.info("浏览器数据目录不存在，无需清理")
                return True
            
            # 获取所有浏览器数据目录
            browser_dirs = [d for d in self.browser_data_dir.iterdir() if d.is_dir()]
            
            if browser_dirs:
                utils.logger.info(f"发现 {len(browser_dirs)} 个浏览器数据目录")
                
                for browser_dir in browser_dirs:
                    utils.logger.info(f"  - 清理浏览器目录: {browser_dir.name}")
                    
                    # 删除目录内容但保留目录本身
                    for item in browser_dir.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                            
                utils.logger.info("浏览器缓存清理完成")
            else:
                utils.logger.info("浏览器数据目录为空，无需清理")
                
            return True
            
        except Exception as e:
            utils.logger.error(f"清理浏览器缓存失败: {e}")
            return False
    
    def clean_proxy_cache(self):
        """清理代理IP缓存"""
        try:
            utils.logger.info("开始清理代理IP缓存...")
            
            # 创建内存缓存实例（代理IP使用内存缓存）
            cache = CacheFactory.create_cache('memory')
            
            # 查找代理IP相关的缓存键
            proxy_keys = cache.keys('*proxy*')
            ip_keys = cache.keys('*ip*')
            kuaidaili_keys = cache.keys('*kuaidaili*')
            jishu_keys = cache.keys('*jishu*')
            
            all_proxy_keys = proxy_keys + ip_keys + kuaidaili_keys + jishu_keys
            
            if all_proxy_keys:
                utils.logger.info(f"发现 {len(all_proxy_keys)} 个代理IP缓存项")
                for key in all_proxy_keys:
                    utils.logger.info(f"  - 清理代理缓存键: {key}")
                # 内存缓存会自动过期
            else:
                utils.logger.info("代理IP缓存为空，无需清理")
                
            utils.logger.info("代理IP缓存清理完成")
            return True
            
        except Exception as e:
            utils.logger.error(f"清理代理IP缓存失败: {e}")
            return False
    
    def clean_all_cache(self):
        """清理所有缓存"""
        utils.logger.info("=" * 50)
        utils.logger.info("开始全面清理缓存...")
        utils.logger.info("=" * 50)
        
        results = []
        
        # 1. 清理内存缓存
        results.append(("内存缓存", self.clean_memory_cache()))
        
        # 2. 清理Redis缓存
        results.append(("Redis缓存", self.clean_redis_cache()))
        
        # 3. 清理浏览器缓存
        results.append(("浏览器缓存", self.clean_browser_cache()))
        
        # 4. 清理代理IP缓存
        results.append(("代理IP缓存", self.clean_proxy_cache()))
        
        # 输出清理结果
        utils.logger.info("=" * 50)
        utils.logger.info("缓存清理结果:")
        utils.logger.info("=" * 50)
        
        success_count = 0
        for cache_type, success in results:
            status = "✓ 成功" if success else "✗ 失败"
            utils.logger.info(f"{cache_type}: {status}")
            if success:
                success_count += 1
        
        utils.logger.info("=" * 50)
        utils.logger.info(f"总计: {success_count}/{len(results)} 项缓存清理成功")
        utils.logger.info("=" * 50)
        
        return success_count == len(results)


def main():
    """主函数"""
    cleaner = CacheCleaner()
    
    print("MediaCrawler 缓存清理工具")
    print("=" * 30)
    print("1. 清理内存缓存")
    print("2. 清理Redis缓存") 
    print("3. 清理浏览器缓存")
    print("4. 清理代理IP缓存")
    print("5. 清理所有缓存")
    print("0. 退出")
    print("=" * 30)
    
    while True:
        try:
            choice = input("请选择操作 (0-5): ").strip()
            
            if choice == "0":
                print("退出缓存清理工具")
                break
            elif choice == "1":
                cleaner.clean_memory_cache()
            elif choice == "2":
                cleaner.clean_redis_cache()
            elif choice == "3":
                cleaner.clean_browser_cache()
            elif choice == "4":
                cleaner.clean_proxy_cache()
            elif choice == "5":
                cleaner.clean_all_cache()
            else:
                print("无效选择，请输入 0-5")
                
        except KeyboardInterrupt:
            print("\n用户中断操作")
            break
        except Exception as e:
            print(f"操作失败: {e}")


if __name__ == "__main__":
    main() 