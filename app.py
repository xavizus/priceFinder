from pricefinder import priceFinder
import json
import pymongo
from datetime import datetime
import config
productsToCheck = [
    {
        "productid": "ST4000NE001",
        "vendors": [
            {"vendor": "dustin",
            "url": "https://www.dustinhome.se/product/5011164597/ironwolf-pro"},
            {"url": "https://www.elgiganten.se/product/datorer-tillbehor/harddisk-ssd-och-nas/149724/seagate-ironwolf-pro-3-5-intern-harddisk-for-nas-4-tb",
            "vendor": "elgiganten"},
            {"url":"https://www.inet.se/produkt/4301688/seagate-ironwolf-pro-4tb-7200rpm-256mb",
            "vendor": "inet"},
            {"url": "https://www.webhallen.com/api/product/312677",
            "vendor": "webhallen"},
            {"url": "https://www.komplett.se/product/1152689/datorutrustning/lagring/haarddisk/haarddisk-35/seagate-ironwolf-pro-4tb-nas-professional",
            "vendor": "komplett"}
        ],
        "productName": "Seagate IronWolf-pro ST4000NE001 128MB 4TB",
        "size": 4
    },
    {
        "productid": "ST6000VN0033",
        "vendors": [
            {"url": "https://www.dustinhome.se/product/5011168946/ironwolf-pro",
            "vendor": "dustin"},
            {"url":"https://www.inet.se/produkt/4301918/seagate-ironwolf-pro-6tb-7200rpm-256mb",
            "vendor": "inet"},
            {"url": "https://www.elgiganten.se/product/datorer-tillbehor/harddisk-ssd-och-nas/149723/seagate-ironwolf-pro-3-5-intern-harddisk-for-nas-6-tb",
            "vendor": "elgiganten"},
            {"url": "https://www.webhallen.com/api/product/312678-Seagate",
            "vendor": "webhallen"},
            {"url": "https://www.komplett.se/product/1152685/datorutrustning/lagring/haarddisk/haarddisk-35/seagate-ironwolf-pro-6tb-nas-professional",
            "vendor": "komplett"}
            
        ],
        "productName": "Seagate IronWolf-pro ST6000VN0033 256MB 6TB",
        "size": 6
    },
    {
        "productid": "ST8000VN004",
        "vendors": [
            {"url": "https://www.dustinhome.se/product/5011160398/ironwolf",
            "vendor": "dustin"},
            {"url": "https://www.elgiganten.se/product/datorer-tillbehor/harddisk-ssd-och-nas/149739/seagate-ironwolf-pro-3-5-intern-harddisk-for-nas-8-tb",
            "vendor": "elgiganten"},
            {"url":"https://www.inet.se/produkt/4301448/seagate-ironwolf-8tb-7200rpm-256mb",
            "vendor": "inet"},
            {"url": "https://www.webhallen.com/api/product/312089",
            "vendor": "webhallen"},
            {"url": "https://www.komplett.se/product/1147206/datorutrustning/lagring/haarddisk/haarddisk-35/seagate-ironwolf-8tb-35-nas-hdd",
            "vendor": "komplett"},
            {"url": "https://www.netonnet.se/art/datorkomponenter/harddisk/sata-35-tum/seagate-ironwolf-st8000vn004-8tb/1009443.8991/",
            "vendor": "netonnet"}
            
        ],
        "productName": "Seagate IronWolf ST8000VN004 256MB 8TB",
        "size": 8
    },
    {
        "productid": "ST10000VN0008",
        "vendors": [
            {"url": "https://www.dustinhome.se/product/5011153178/ironwolf",
            "vendor": "dustin"},
            {"url": "https://www.elgiganten.se/product/datorer-tillbehor/harddisk-ssd-och-nas/157258/seagate-ironwolf-3-5-intern-hdd-for-nas-10-tb",
            "vendor": "elgiganten"},
            {"url":"https://www.inet.se/produkt/4300258/seagate-ironwolf-4tb-5900rpm-64mb",
            "vendor": "inet"},
            {"url": "https://www.webhallen.com/api/product/314439",
            "vendor": "webhallen"},
            {"url": "https://www.komplett.se/product/1146023/datorutrustning/lagring/haarddisk/haarddisk-35/seagate-ironwolf-10tb-35-nas-hdd",
            "vendor": "komplett"},
            {"url": "https://www.netonnet.se/art/datorkomponenter/harddisk/sata-35-tum/seagate-ironwolf-st10000vn0008-10tb/1010198.8991/",
            "vendor": "netonnet"}
        ],
        "productName": "Seagate IronWolf ST10000VN0008 256MB 10TB",
        "size": 10
    }
]

prices = priceFinder(productsToCheck)

data = prices.getProducts()

dbClient = pymongo.MongoClient(config.MONGODB)
mydb = dbClient['pricefinder']
myCol = mydb['products']
collections = mydb.list_collection_names()

if 'products' not in collections:
    ids = myCol.insert_many(data)
    print("Collection \"products\" is empty, filling with the current data. Nothing more to do.")
    print(ids.inserted_ids)
    raise SystemExit(0)

for product in data:
    for vendor in product['vendors']:
        vendorDBData = myCol.find_one({'productid': product['productid'], "vendors.vendor": vendor['vendor']}, {"_id": 0, "vendors.$": 1})
        vendorDBPrice = vendorDBData['vendors'][0]['price']
        myCol.update_one({'productid': product['productid'], "vendors.vendor": vendor['vendor']}, { "$set": { "vendors.$.price": vendor['price'] }, "$push": {"vendors.$.oldPrices": {"date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "price": vendorDBPrice}}})
       