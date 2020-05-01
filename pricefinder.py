import requests
from bs4 import BeautifulSoup as BS
from typing import Type
import re
import utils
import pymongo
import config
from datetime import datetime

class priceFinder:

    def __init__(self, products: dict, testData=False):
        self.products = testData or products
        if not testData:
            self.addPriceToProducts()
        
        dbClient = pymongo.MongoClient(config.MONGODB)
        self.db = dbClient['pricefinder']
        self.dbCol = self.db['products']


        if not self.collectionExists('products'):
            self.dbCol.insert_many(self.products)
            print("Collection \"products\" is empty, filling with the current data.")
        else:
            self.updatePricesInDB()
        self.lowestPrices = self.getLowestPricesForEachProduct()
        self.setLowestPriceInDB()
    
    def setLowestPriceInDB(self):
        for productIndex, product in enumerate(self.lowestPrices):
            oldData = self.dbCol.find_one_and_update({"productid": product['productid']}, {"$set" : {"lowestPrice": product['price']}}, {"productid": 1, "lowestPrice": 1})
            print(oldData)
            if 'lowestPrice' in oldData:
                self.lowestPrices[productIndex]['oldPrice'] = oldData['lowestPrice']
            else:
                self.lowestPrices[productIndex]['oldPrice'] = None

    def getLowestPricesForEachProduct(self) -> list:
        lowestPrices = []
        # Credits to following site: 
        # https://techbrij.com/mongodb-aggregation-query-records-max
        for lowestPrice in self.dbCol.aggregate(
            [
	            {"$unwind": "$vendors"},
	            {	
		            "$group": {
			            "_id": "$_id",
			            "minPrice": {
				            "$min": "$vendors.price"
			            },
			            "productGroup": {
				            "$push": {
					            "productid": "$productid",
					            "productName": "$productName",
					            "vendor": "$vendors.vendor",
					            "price": "$vendors.price",
					            "url": "$vendors.url",
                                "size": "$size"
				            }
			            }
		            }
	            },
	            {
		            "$project": {
			            "_id": 0,
			            "toppers": {
				            "$setDifference": [
                                {
					                "$map": {
						                "input": "$productGroup",
						                "as": "product",
						                "in": {
							                "$cond": [
								                {
									                "$eq": ["$minPrice", "$$product.price"]
								                },
								                "$$product",
								                "false"
							                ]
						                }
					                }
				                },
                                ["false"]
                            ]
			            }
		            }
	            },
	            {
		            "$unwind": "$toppers"
	            },
	            {
		            "$project": {
			            "productid": "$toppers.productid",
			            "productName": "$toppers.productName",
			            "vendor": "$toppers.vendor",
			            "price": "$toppers.price",
			            "url": "$toppers.url",
                        "size": "$toppers.size"
		            }
	            }
            ]
        ):
            lowestPrices.append(lowestPrice)

        return lowestPrices

    def collectionExists(self, collectionName) -> bool:
        if collectionName in  self.db.list_collection_names():
            return True
        else:
            return False

    def updatePricesInDB(self):
        for product in self.products:
            for vendor in product['vendors']:
                vendorDBData = self.dbCol.find_one({'productid': product['productid'], "vendors.vendor": vendor['vendor']}, {"_id": 0, "vendors.$": 1})
                vendorDBPrice = vendorDBData['vendors'][0]['price']
                self.dbCol.update_one({'productid': product['productid'], "vendors.vendor": vendor['vendor']}, { "$set": { "vendors.$.price": vendor['price'] }, "$push": {"vendors.$.oldPrices": {"date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "price": vendorDBPrice}}})
       

    def addPriceToProducts(self):
        for productIndex, product in enumerate(self.products):
            for vendorIndex, vendor in enumerate(product['vendors']):
                price = self.getCost(vendor['vendor'], vendor['url'])
                self.products[productIndex]['vendors'][vendorIndex]['price'] = price

    def getProducts(self):
        return self.products
    def getCost(self, vendor, url) -> int:
        response = requests.get(url)
        if vendor != "webhallen":
            soup = BS(response.content, 'html.parser')
        
        if vendor == "webhallen":
            price = self.getCostWebhallen(response)
        elif vendor in ('dustin', 'inet'):
            price = self.getCostDustinOrInet(soup)
        elif vendor == "elgiganten":
            price = self.getCostElgiganten(soup)
        elif vendor == "komplett":
            price = self.getCostKomplett(soup)
        elif vendor == "netonnet":
            price = self.getCostNetonnet(soup)

        try:
            price = int(price)
        except ValueError:
            try:
                price = int(float(price))
            except ValueError:
                price = 0
        
        return price

    def getCostNetonnet(self, soup: Type[BS]) -> int:
        results = soup.find_all('div', class_="price-big")
        price = utils.remove_white_space(results[0].text).replace(":-", "")
        return price
    def getCostDustinOrInet(self, soup: Type[BS]) -> int:
        results = soup.find_all('span', class_="price")
        price = utils.remove_white_space(results[0].text).replace("kr", "")
        return price

    def getCostElgiganten(self, soup: Type[BS]):
        results = soup.find_all('div', class_="product-price-container")
        price = utils.remove_white_space(utils.remove_html_tags(results[0].text))
        return price

    def getCostWebhallen(self, response):
        data = response.json()
        price = data['product']['price']['price']
        return price

    def getCostKomplett(self, soup: Type[BS]):
        results = soup.find_all('span', class_="product-price-now")
        price = utils.remove_white_space(utils.remove_html_tags(results[0].text)).replace(':-', '')
        return price