import requests
from bs4 import BeautifulSoup as BS
from typing import Type
import re
import utils

class priceFinder:

    def __init__(self, products: dict):
        self.products = products

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