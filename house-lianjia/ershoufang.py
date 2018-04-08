import setting
import logging
import crawlcore
from bs4 import BeautifulSoup
import model
import time
import datetime

logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S', filename='result.log', filemode='w')
BASE_URL = "http://hz.lianjia.com/"


def GetHouseByRegionlist():
    starttime = datetime.datetime.now()
    url = BASE_URL + "ershoufang"
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    region_list = soup.find('div', {'data-role': 'ershoufang'}).findAll('a')
    if region_list is None:
        raise RuntimeError('url:【%s】未找到region_list' % url)
    for regionlink in region_list:
        logging.info("Get Onsale House Infomation in %s" % regionlink.get_text())
        try:
            get_house_perregion(regionlink.get('href'))
        except Exception as e:
            logging.error(e)
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))

def get_house_perregion(link):
    url = BASE_URL + link
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    total_pages = crawlcore.get_total_pages(soup)
    if total_pages is None:
        raise RuntimeError('url:【%s】未找到total_pages' % url)

    for page in range(1, total_pages + 1):
        if page > 1:
            url_page = url + u"/pg%d/" % page
            source_code = crawlcore.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        logging.info("GetHouseByRegionlist district:%s page:%s totalpage:%s" % (link, page, total_pages))
        data_source = []
        hisprice_data_source = []
        for ultag in soup.findAll("ul", {"class":"sellListContent"}):
            for name in ultag.find_all('li'):
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"title"})
                    info_dict.update({'title':housetitle.get_text().strip()})
                    info_dict.update({'link':housetitle.a.get('href')})
                    houseID = housetitle.a.get('data-housecode')
                    if houseID is None:
                        houseID = housetitle.a.get('data-lj_action_housedel_id')
                    info_dict.update({'houseID':houseID})

                    houseinfo = name.find("div", {"class":"houseInfo"})
                    info = houseinfo.get_text().split('|')

                    # logging.info('houseID: %s houseinfo: %s' % (houseID,info))

                    info_dict.update({'community':info[0]})
                    info_dict.update({'housetype':info[1]})
                    info_dict.update({'square':info[2]})
                    info_dict.update({'direction':info[3]})
                    info_dict.update({'decoration':info[4]})

                    housefloor = name.find("div", {"class":"positionInfo"})
                    info_dict.update({'years':housefloor.get_text().strip()})
                    info_dict.update({'floor':housefloor.get_text().strip()})

                    followInfo = name.find("div", {"class":"followInfo"})
                    info_dict.update({'followInfo':followInfo.get_text().strip()})

                    taxfree = name.find("span", {"class":"taxfree"})
                    if taxfree == None:
                        info_dict.update({"taxtype":""})
                    else:
                        info_dict.update({"taxtype":taxfree.get_text().strip()})

                    totalPrice = name.find("div", {"class":"totalPrice"})
                    info_dict.update({'totalPrice':totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class":"unitPrice"})
                    info_dict.update({'unitPrice':unitPrice.get("data-price")})

                    info_dict.update({'version': setting.DB_VERSION})
                except:
                    continue
                # Houseinfo insert into mysql
                data_source.append(info_dict)
                hisprice_data_source.append({"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"],
                                             'version': setting.DB_VERSION})

        with model.database.atomic():
            model.Houseinfo.insert_many(data_source).execute()
            model.Hisprice.insert_many(hisprice_data_source).execute()
        time.sleep(1)
