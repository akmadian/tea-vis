import sys
import string
import json
import time
import csv
import os.path
import urllib.request
from urllib.error import HTTPError
from optparse import OptionParser

PRODUCT_GROUP_IDS = {
    "Pu Erh": 1,
    "Black": 2,
    "Oolong": 3,
    "Green": 4,
    "Yellow": 5,
    "White": 6,
    "Sheng": 7,
    "Shou": 8
}

COLLECTION = 0
CATEGORY = 1
NAME = 2
VARIANT_NAME = 3
PRICE = 4
IN_STOCK = 5
URL = 6
ID = 7



class ProductCatalog:
    def __init__(self):
        self.products = []

    def addProduct(self, product):
        self.products.append(product)

    def buildD3(self):
        return {
            'nodes': self.buildNodes(),
            'links': self.buildLinks()
        }
    
    def buildCSV(self):
        path = 'C:/src/tea-vis/src/data/clcatalog-nv.csv'
        with open(path, 'w', newline="", encoding="utf-8") as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow(['size', 'path'])
            writer.writerow(['', 'YunnanSourcing'])
            writer.writerow(['', 'YunnanSourcing/PuErh'])
            writer.writerow(['', 'YunnanSourcing/PuErh/Sheng'])
            writer.writerow(['', 'YunnanSourcing/PuErh/Shou'])
            writer.writerow(['', 'YunnanSourcing/Black'])
            writer.writerow(['', 'YunnanSourcing/White'])
            writer.writerow(['', 'YunnanSourcing/Yellow'])
            writer.writerow(['', 'YunnanSourcing/Green'])
            writer.writerow(['', 'YunnanSourcing/Oolong'])
            writer.writerow(['', 'YunnanSourcing/Teaware'])

            for product in self.products:
                if product.path.split('/')[1] == 'PuErh':
                    if len(product.path.split('/')) == 4:
                        writer.writerow(['', product.path])
                else:
                    if len(product.path.split('/')) == 3:
                        writer.writerow(['', product.path])


    def export(self):
        with open('C:/src/tea-vis/src/data/yscatalog-tree.json', 'w') as exportFile:
            json.dump(self.buildD3(), exportFile)

class YSProduct:
    def __init__(self, path, id):
        self.id = id
        self.path = path
        self.level = len(path.split('/'))

PRODUCT_CATALOG = ProductCatalog()

def standardizeCategory(productType):
        lower = productType.lower()
        if ('ripe' in lower or 'shou' in lower): return 'Shou'
        elif ('raw' in lower or 'sheng' in lower): return 'Sheng'
        elif ('oolong' in lower): return 'Oolong'
        elif ('black' in lower): return 'Black'
        elif ('white' in lower): return 'White'
        elif ('yellow' in lower): return 'Yellow'
        elif ('green' in lower): return 'Green'
        else: 
            return 'Teaware'

def isPuErh(type_):
    if "Pu-erh" in type_ or "Raw" in type_ or "Ripe" in type_ or 'Sheng' in type_ or 'Shou' in type_:
        return True
    else:
        return False

def genPath(name, type_, variantName):
    teaType = standardizeCategory(type_) if not isPuErh(type_) else "PuErh/{}".format(standardizeCategory(type_))
    basePath = "YunnanSourcing/{}".format(teaType.strip())
    if variantName:
        return str(''.join(char for char in '{}/{}/{}'.format(basePath, name.replace(type_, '').replace('/', ''), variantName.replace('/', '')) if ord(char) < 128).replace('"', ''))
    else:
        return str(''.join(char for char in '{}/{}'.format(basePath, name.replace(type_, '').replace('/', '')) if ord(char) < 128).replace('"', ''))
        

with open('products-cl.csv', newline='', encoding='utf-8') as productCSV:
    reader = csv.reader(productCSV)
    seenProducts = set()
    for row in reader:
        print(row)
        if not row[NAME] in seenProducts: # if product has not been seen before
            product = YSProduct(
                genPath(
                    row[NAME],
                    row[CATEGORY],
                    False
                ),
                row[ID]
            )
            PRODUCT_CATALOG.addProduct(product)

            varProduct = YSProduct(
                genPath(
                    row[NAME],
                    row[CATEGORY],
                    row[VARIANT_NAME]
                ),
                row[ID]
            )
            PRODUCT_CATALOG.addProduct(varProduct)
        else:
            varProduct = YSProduct(
                genPath(
                    row[NAME],
                    row[CATEGORY],
                    row[VARIANT_NAME]
                ),
                row[ID]
            )
            PRODUCT_CATALOG.addProduct(varProduct)

        seenProducts.add(row[NAME])
    
    PRODUCT_CATALOG.buildCSV()
