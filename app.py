from pricefinder import priceFinder
import json
import pymongo
from datetime import datetime
import config
import requests
productsToCheck = [
    {
        "productid": "ST4000NE001",
        "vendors": [
            {"vendor": "dustin",
             "url": "https://www.dustinhome.se/product/5011164597/ironwolf-pro"},
            {"url": "https://www.elgiganten.se/product/datorer-tillbehor/harddisk-ssd-och-nas/149724/seagate-ironwolf-pro-3-5-intern-harddisk-for-nas-4-tb",
             "vendor": "elgiganten"},
            {"url": "https://www.inet.se/produkt/4301688/seagate-ironwolf-pro-4tb-7200rpm-256mb",
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
            {"url": "https://www.inet.se/produkt/4301918/seagate-ironwolf-pro-6tb-7200rpm-256mb",
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
            {"url": "https://www.inet.se/produkt/4301448/seagate-ironwolf-8tb-7200rpm-256mb",
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
            {"url": "https://www.inet.se/produkt/4301922/seagate-ironwolf-10tb-7200rpm-256mb",
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

# Rate-Limit: 5 requests per 3 seconds
def sendDiscordMessage(content):

    content['oldPrice'] = content['oldPrice'] if content['oldPrice'] else "-"
    if content['oldPrice'] == '-':
        content['priceDiff'] = '-'
    else:
        content['priceDiff'] = (1-(content['price']/content['oldPrice']))*100
    
    payload = {
        "file": "content",
        "embeds": [
            {
                "title": f"Prices for hardrive with {content['size']} TB storage",
                "fields": [
                    {
                        "name": "Product",
                        "value": content['productName'],
                        "inline": True
                    },
                    {
                        "name": "Where",
                        "value": content['vendor'],
                        "inline": True
                    },
                    {
                        "name": "Price",
                        "value": content['price'],
                        "inline:": True
                    },
                    {
                        "name": "Old price",
                        "value": content['oldPrice'],
                        "inline": True
                    },
                    {
                        "name": "Price Diffrence",
                        "value": f"{content['priceDiff']} %",
                    },
                    {
                        "name": "URL",
                        "value": f"[{content['vendor']}]({content['url']})"
                    }
                ]
            }
        ]
    }
    if content['priceDiff'] == '-':
        pass
    elif content['priceDiff'] > 0:
        payload['embeds'][0]['color'] = 2067276
        payload['content'] = "A lower price have been found! <@&182749298390204416>"
    elif content['priceDiff'] < 0:
        payload['embeds'][0][3]['value'] = f"{((content['price'] - content['oldprice'])/content['price'])*100} %"
        payload['embeds'][0]['color'] = 10038562

    response = requests.post(config.DISCORD_WEBHOOK, json=payload)
    if response.status_code in [200, 204]:
        print("Discord Message sent!")
    else:
        print(f"Something went wrong! Code: {response.status_code}")


prices = priceFinder(productsToCheck)

for product in prices.lowestPrices:
    sendDiscordMessage(product)
