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


def GetRentByRegionlist():
    starttime = datetime.datetime.now()

    url = BASE_URL + "zufang"
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    region_list = soup.find('dd', {'data-index':'0'}).findAll('a')

    for regionlink in region_list:
        if regionlink.get_text() != '不限':
            logging.info("Get Rent House Infomation in %s" % regionlink.get_text())
            try:
                get_rent_perregion(regionlink.get('href'))
            except Exception as e:
                logging.error(e)
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))


def get_rent_perregion(link):
    url = BASE_URL + link
    source_code = crawlcore.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    total_pages = crawlcore.get_total_pages(soup)
    if total_pages is None:
        raise RuntimeError('url:【%s】未找到total_pages' % url)

    for page in range(1, total_pages + 1):
        if page > 1:
            url_page = url + u"/pg%d/" %  page
            source_code = crawlcore.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        logging.info("GetRentByRegionlist district:%s page:%s totalpage:%s" % (link, page, total_pages))
        data_source = []

        for ultag in soup.findAll("ul", {"class":"house-lst"}):
            for name in ultag.find_all('li'):

                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"info-panel"})
                    info_dict.update({'title':housetitle.h2.a.get_text().strip()})

                    info_dict.update({'link':housetitle.a.get("href")})

                    houseID = name.get("data-housecode")
                    info_dict.update({'houseID':houseID})

                    region = name.find("span", {"class":"region"})
                    info_dict.update({'region':region.get_text().strip()})

                    zone = name.find("span", {"class":"zone"})
                    info_dict.update({'zone':zone.get_text().strip()})

                    meters = name.find("span", {"class":"meters"})
                    info_dict.update({'meters':meters.get_text().strip()})

                    other = name.find("div", {"class":"con"})
                    info_dict.update({'other':other.get_text().strip()})

                    subway = name.find("span", {"class":"fang-subway-ex"})
                    if subway is None:
                        info_dict.update({'subway':""})
                    else:
                        info_dict.update({'subway':subway.span.get_text().strip()})

                    decoration = name.find("span", {"class":"decoration-ex"})
                    if decoration is None:
                        info_dict.update({'decoration': ""})
                    else:
                        info_dict.update({'decoration':decoration.span.get_text().strip()})

                    heating = name.find("span", {"class":"heating-ex"})
                    if heating is None:
                        info_dict.update({'heating': ""})
                    else:
                        info_dict.update({'heating':heating.span.get_text().strip()})

                    price = name.find("div", {"class":"price"})
                    info_dict.update({'price':int(float(price.span.get_text().strip()))})

                    pricepre = name.find("div", {"class":"price-pre"})
                    info_dict.update({'pricepre':pricepre.get_text().strip()})

                    info_dict.update({'version': setting.DB_VERSION})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)


        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).execute()
        time.sleep(1)

