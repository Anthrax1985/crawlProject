import setting
import model
import logging
# import community
import community_multi
import ershoufang_multi
import rentHouse_multi

logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S', filename='result.log', filemode='w')

if __name__ == '__main__':
    logging.info('===============开始本次爬取作业，本次VERSION为【%s】=============' % setting.DB_VERSION)
    # 初始化DB表结构
    model.database_init()
    # 爬取杭州所有的小区名
    # community_multi.get_community()
    # 爬取杭州所有的二手房信息
    # ershoufang_multi.GetHouseByRegionlist()
    # 爬取杭州所有的租房信息
    rentHouse_multi.GetRentByRegionlist()


