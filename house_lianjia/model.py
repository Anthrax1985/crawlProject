import setting
import datetime
from peewee import *
import logging

logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%a, %d %b %Y %H:%M:%S', filename='result.log', filemode='w')


if setting.DB_TYPE == 'mysql':
    database = MySQLDatabase(
        setting.DB_NAME,
        host=setting.DB_HOST,
        port=setting.DB_PORT,
        user=setting.DB_USER,
        passwd=setting.DB_PASSWORD,
        charset='utf8mb4',
        use_unicode=True,
    )

elif setting.DB_TYPE == 'postgresql':
    database = PostgresqlDatabase(
        setting.DB_NAME,
        user=setting.DB_USER,
        password=setting.DB_PASSWORD,
        host=setting.DB_HOST,
        charset='utf8',
        use_unicode=True,
    )
elif setting.DB_TYPE == 'sqlite3':
    database = SqliteDatabase(setting.DB_NAME)

else:
    raise AttributeError("DB_TYPE in setting.py is wrong.[%s]" % setting.DB_TYPE)


class BaseModel(Model):
    class Meta:
        database = database


class Community(BaseModel):
    id          = BigAutoField()
    communityid = BigIntegerField()
    title 		= CharField()
    link 		= CharField(unique=True)
    district 	= CharField()
    bizcircle 	= CharField()
    tagList 	= CharField()
    onsale 		= CharField()
    onrent 		= CharField(null=True)
    year        = CharField(null=True)
    housetype   = CharField(null=True)
    cost        = CharField(null=True)
    service		= CharField(null=True)
    company     = CharField(null=True)
    building_num= CharField(null=True)
    house_num   = CharField(null=True)
    price   	= CharField(null=True)
    version     = CharField()
    validdate 	= DateTimeField(default=datetime.datetime.now)


class Houseinfo(BaseModel):
    id          = BigAutoField()
    houseID 	= CharField()
    title 		= CharField()
    link 		= CharField()
    community 	= CharField()
    years 		= CharField()
    housetype 	= CharField()
    square 		= CharField()
    direction 	= CharField()
    floor 		= CharField()
    taxtype 	= CharField()
    totalPrice 	= CharField()
    unitPrice 	= CharField()
    followInfo 	= CharField()
    decoration 	= CharField()
    version     = CharField()
    validdate 	= DateTimeField(default=datetime.datetime.now)


class Hisprice(BaseModel):
    id          = BigAutoField()
    houseID 	= CharField()
    totalPrice 	= CharField()
    date 		= DateTimeField(default=datetime.datetime.now)
    version     = CharField()


class Sellinfo(BaseModel):
    id          = BigAutoField()
    houseID 	= CharField()
    title 		= CharField()
    link 		= CharField()
    community 	= CharField()
    years 		= CharField()
    housetype 	= CharField()
    square 		= CharField()
    direction 	= CharField()
    floor 		= CharField()
    status 		= CharField()
    source 		= CharField()
    totalPrice 	= CharField()
    unitPrice 	= CharField()
    dealdate 	= CharField(null=True)
    version     = CharField()
    updatedate 	= DateTimeField(default=datetime.datetime.now)


class Rentinfo(BaseModel):
    id          = BigAutoField()
    houseID 	= CharField()
    title 		= CharField()
    link 		= CharField()
    region 		= CharField()
    zone 		= CharField()
    meters 		= CharField()
    other 		= CharField()
    subway 		= CharField()
    decoration 	= CharField()
    heating 	= CharField()
    price 		= CharField()
    pricepre 	= CharField()
    version     = CharField()
    updatedate 	= DateTimeField(default=datetime.datetime.now)


def database_init():
    database.connect()
    database.create_tables([Community, Houseinfo, Hisprice, Sellinfo, Rentinfo], safe=True)
    database.close()