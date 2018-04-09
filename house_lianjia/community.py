import datetime
import setting
import logging
import crawlcore
from bs4 import BeautifulSoup
import model
import time


logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S', filename='result.log', filemode='w')
BASE_URL = "http://hz.lianjia.com/"
Community_Key_Pool = []

def get_community():
    # 通过链家 [小区] 连接获得所有小区的信息
    # 由于链家的列表最大显示100页
    # 通过以下方法获取最大限度数据
    # 1.获取来自所有列表的小区信息【0-100页】 https://hz.lianjia.com/xiaoqu/?from=rec
    # 2.通过遍历区域来获得小区信息
    # 3.通过小区均价的正反排序来获得更多的小区数据
    #   通过成交量的正反排序来获得更多的小区数据
    starttime = datetime.datetime.now()
    logging.info('get_community 获取杭州所有小区的数据')
    get_community_from_default_all()
    get_community_from_region_list()
    get_community_from_rank_list()
    endtime = datetime.datetime.now()
    logging.info("get_community Run time: " + str(endtime - starttime)
                 + " Total:" + len(Community_Key_Pool))


def get_community_from_default_all():
    starttime = datetime.datetime.now()
    logging.info('get_community_from_default_all 获取来自所有列表的小区信息')
    url = BASE_URL + "xiaoqu/?from=rec"
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    total_pages = crawlcore.get_total_pages(soup)

    if total_pages is None:
        raise RuntimeError('url:【%s】未找到total_pages' % url)

    for page in range(1, total_pages + 1):
        if page > 1:
            sub_url = BASE_URL + "xiaoqu/pg%s" % page
            source_code = crawlcore.get_source_code(sub_url)
            soup = BeautifulSoup(source_code, 'lxml')

        name_list = soup.findAll('li', {'class': 'clear xiaoquListItem'})
        logging.info('get_community_from_default_all page:%s total_page:%s' % (page, total_pages))
        for name in name_list:
            info_dict = {}
            try:
                communitytitle = name.find("div", {"class": "title"})
                title = communitytitle.get_text().strip('\n')

                if title in Community_Key_Pool:
                    continue
                Community_Key_Pool.append(title)
                link = communitytitle.a.get('href')
                info_dict.update({'title': title})
                info_dict.update({'link': link})

                district = name.find("a", {"class": "district"})
                info_dict.update({'district': district.get_text()})

                bizcircle = name.find("a", {"class": "bizcircle"})
                info_dict.update({'bizcircle': bizcircle.get_text()})

                tagList = name.find("div", {"class": "tagList"})
                info_dict.update({'tagList': tagList.get_text().strip('\n')})

                onsale = name.find("a", {"class": "totalSellCount"})
                info_dict.update({'onsale': onsale.span.get_text().strip('\n')})

                onrent = name.find("a", {"title": title + u"租房"})
                info_dict.update({'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

                info_dict.update({'communityid': name.get('data-housecode')})

                price = name.find("div", {"class": "totalPrice"})
                info_dict.update({'price': price.span.get_text().strip('\n')})

                info_dict.update({'version': setting.DB_VERSION})

                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.items():
                    info_dict.update({key: value})
                with model.database.atomic():
                    model.Community.insert(info_dict).execute()
                time.sleep(1)
            except:
                continue
    endtime = datetime.datetime.now()
    logging.info("get_community_from_default_all Run time: " + str(endtime - starttime)
                 + " Total:" + len(Community_Key_Pool))


def get_community_from_region_list():
    starttime = datetime.datetime.now()
    logging.info('get_community_from_region_list 获取来自所有列表的小区信息')
    url = BASE_URL + "xiaoqu/?from=rec"
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    region_list = soup.find('div', {'data-role': 'ershoufang'}).findAll('a')

    if region_list is None:
        raise RuntimeError('url:【%s】未找到region_list' % url)

    for region in region_list:
        sub_region_url = BASE_URL + region.get('href')
        source_code = crawlcore.get_source_code(sub_region_url)
        soup = BeautifulSoup(source_code, 'lxml')

        total_pages = crawlcore.get_total_pages(soup)

        if total_pages is None:
            raise RuntimeError('url:【%s】未找到total_pages' % url)

        for page in range(1, total_pages + 1):
            # for page in {1, total_pages}:
            if page > 1:
                sub_url = sub_region_url + "/pg%s" % page
                source_code = crawlcore.get_source_code(sub_url)
                soup = BeautifulSoup(source_code, 'lxml')

            name_list = soup.findAll('li', {'class': 'clear xiaoquListItem'})
            logging.info('get_community_from_region_list page:%s total_page:%s'
                         % (page, total_pages))
            for name in name_list:
                info_dict = {}
                try:
                    communitytitle = name.find("div", {"class": "title"})
                    title = communitytitle.get_text().strip('\n')
                    if title in Community_Key_Pool:
                        continue
                    Community_Key_Pool.append(title)
                    link = communitytitle.a.get('href')
                    info_dict.update({'title': title})
                    info_dict.update({'link': link})

                    district = name.find("a", {"class": "district"})
                    info_dict.update({'district': district.get_text()})

                    bizcircle = name.find("a", {"class": "bizcircle"})
                    info_dict.update({'bizcircle': bizcircle.get_text()})

                    tagList = name.find("div", {"class": "tagList"})
                    info_dict.update({'tagList': tagList.get_text().strip('\n')})

                    onsale = name.find("a", {"class": "totalSellCount"})
                    info_dict.update({'onsale': onsale.span.get_text().strip('\n')})

                    onrent = name.find("a", {"title": title + u"租房"})
                    info_dict.update({'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

                    info_dict.update({'communityid': name.get('data-housecode')})

                    price = name.find("div", {"class": "totalPrice"})
                    info_dict.update({'price': price.span.get_text().strip('\n')})

                    info_dict.update({'version': setting.DB_VERSION})

                    communityinfo = get_communityinfo_by_url(link)
                    for key, value in communityinfo.items():
                        info_dict.update({key: value})
                    with model.database.atomic():
                        model.Community.insert(info_dict).execute()
                    time.sleep(1)
                except:
                    continue
    endtime = datetime.datetime.now()
    logging.info("get_community_from_region_list Run time: " + str(endtime - starttime)
                 + " Total:" + len(Community_Key_Pool))


def get_community_from_rank_list():
    starttime = datetime.datetime.now()
    logging.info('get_community_from_rank_list 获取来自所有列表的小区信息')
    for sort in {'cro21', 'cro22', 'cro11', 'cro12'}:
        url = BASE_URL + "xiaoqu/" + sort
        source_code = crawlcore.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')
        total_pages = crawlcore.get_total_pages(soup)

        if total_pages is None:
            raise RuntimeError('url:【%s】未找到total_pages' % url)

        for page in range(1, total_pages + 1):
            # for page in {1, total_pages}:
            if page > 1:
                sub_url = BASE_URL + "xiaoqu/pg%s" % page
                source_code = crawlcore.get_source_code(sub_url)
                soup = BeautifulSoup(source_code, 'lxml')

            name_list = soup.findAll('li', {'class': 'clear xiaoquListItem'})
            logging.info('get_community_from_rank_list sort:%s page:%s total_page:%s' % (sort, page, total_pages))
            for name in name_list:
                info_dict = {}
                try:
                    communitytitle = name.find("div", {"class": "title"})
                    title = communitytitle.get_text().strip('\n')
                    if title in Community_Key_Pool:
                        continue
                    Community_Key_Pool.append(title)
                    link = communitytitle.a.get('href')
                    info_dict.update({'title': title})
                    info_dict.update({'link': link})

                    district = name.find("a", {"class": "district"})
                    info_dict.update({'district': district.get_text()})

                    bizcircle = name.find("a", {"class": "bizcircle"})
                    info_dict.update({'bizcircle': bizcircle.get_text()})

                    tagList = name.find("div", {"class": "tagList"})
                    info_dict.update({'tagList': tagList.get_text().strip('\n')})

                    onsale = name.find("a", {"class": "totalSellCount"})
                    info_dict.update({'onsale': onsale.span.get_text().strip('\n')})

                    onrent = name.find("a", {"title": title + u"租房"})
                    info_dict.update({'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

                    info_dict.update({'communityid': name.get('data-housecode')})

                    price = name.find("div", {"class": "totalPrice"})
                    info_dict.update({'price': price.span.get_text().strip('\n')})

                    info_dict.update({'version': setting.DB_VERSION})

                    communityinfo = get_communityinfo_by_url(link)
                    for key, value in communityinfo.items():
                        info_dict.update({key: value})
                    with model.database.atomic():
                        model.Community.insert(info_dict).execute()
                    time.sleep(1)
                except:
                    continue

    endtime = datetime.datetime.now()
    logging.info("get_community_from_rank_list Run time: " + str(endtime - starttime)
                 + " Total:" + len(Community_Key_Pool))


def get_communityinfo_by_url(url):
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    communityinfos = soup.findAll("div", {"class": "xiaoquInfoItem"})
    res = {}
    for info in communityinfos:
        key_type = {
            u"建筑年代": "year",
            u"建筑类型": "housetype",
            u"物业费用": "cost",
            u"物业公司": "service",
            u"开发商": "company",
            u"楼栋总数": "building_num",
            u"房屋总数": "house_num",
        }
        try:
            key = info.find("span", {"xiaoquInfoLabel"})
            value = info.find("span", {"xiaoquInfoContent"})
            key_info = key_type[key.get_text().strip()]
            value_info = value.get_text().strip()
            res.update({key_info: value_info})
        except:
            continue

    return res
