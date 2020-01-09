import sys
import string
import json
import time
import csv
import os.path
import urllib.request
from urllib.error import HTTPError
from optparse import OptionParser


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
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


class ProductCatalog:
    def __init__(self):
        self.products = []

    def buildD3(self):
        return {
            'nodes': self.buildNodes(),
            'links': self.buildLinks()
        }
    
    def buildCSV(self):
        path = 'C:/src/tea-vis/src/data/yscatalog-tree3.csv'
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
                if product.standardType != 'Teaware' and not 'mang' in product.name and not 'Mang' in product.name:
                    teaType = product.standardType if not self.isPuErh(product.standardType) else "PuErh/{}".format(product.standardType)
                    path = "YunnanSourcing/{}/{}".format(teaType.strip(), product.name.strip())
                    writer.writerow(['', path])

                    """
                    for variant in product.variants:
                        variantPath = "{}/{}".format(path.strip(), variant['option1'].replace('/', ' ').strip())

                        writer.writerow(['', variantPath])"""

    def isPuErh(self, teaType):
        if "Sheng" in teaType or "Shou" in teaType or "Pu Erh" in teaType:
            return True
        else:
            return False

    def sanitize(self, toSanitize):
        allASCII = ''.join(char for char in toSanitize if ord(char) < 128)
        stripped = allASCII.replace(' ', '').replace('"', '')
        return stripped

    def buildNodesJson(self):
        nodes = [
            {"name": "YunnanSourcing.com", "level": 0, 'id': 0},
            {"name": "Pu Erh", "level": 1, 'id': 1},
            {"name": "Black", "level": 1, 'id': 2},
            {"name": "Oolong", "level": 1, 'id': 3},
            {"name": "Green", "level": 1, 'id': 4},
            {"name": "Yellow", "level": 1, 'id': 5},
            {"name": "White", "level": 1, 'id': 6},
            {"name": "Sheng", "level": 2, 'id': 7},
            {"name": "Shou", "level": 2, 'id': 8}
        ]

        for product in self.products:
            try:
                nodes.append({
                    "name": product.name,
                    "level": 3,
                    'id': product.id,
                    'parentId': PRODUCT_GROUP_IDS[product.standardType]
                })

                for variant in product.variants:
                    nodes.append({
                        "name": variant['title'],
                        "level": 4,
                        'id': variant['id']
                    })
            except KeyError:
                print('KeyError Caught')
            except AttributeError:
                print('AttributeError Caught')

        return nodes

    def buildLinksJson(self):
        links = []

        for i in range(1, 7):
            links.append({
                'source': 0,
                'dest': i
            })

        links.append({'source': 1, 'dest': 7})
        links.append({'source': 1, 'dest': 8})

        for product in self.products:
            try:
                if (product.standardType is not None):
                    links.append({
                        'source': PRODUCT_GROUP_IDS[product.standardType],
                        'dest': product.id
                    })
                    for variant in product.variants:
                        links.append({
                            'source': product.id,
                            'dest': variant['id']
                        })
            except KeyError:
                print('KeyError Caught')
            except AttributeError:
                print('AttributeError Caught')

        return links

    def export(self):
        with open('C:/src/tea-vis/src/data/yscatalog-tree.json', 'w') as exportFile:
            json.dump(self.buildD3(), exportFile)

    def numProducts(self, includeVariants = True):
        num = 0
        for product in self.products:
            num += 1
            num += len(product.variants)

        return num


class YSProduct:
    def __init__(self, product):
        self.id = product['id']
        self.name = self.formatName(product['title'])
        self.standardType = self.standardizeCataegory(product['product_type'])
        self.variants = product['variants']

    def standardizeCataegory(self, productType):
        lower = productType.lower()
        if ('ripe' in lower): return 'Shou'
        elif ('raw' in lower): return 'Sheng'
        elif ('oolong' in lower): return 'Oolong'
        elif ('black' in lower): return 'Black'
        elif ('white' in lower): return 'White'
        elif ('yellow' in lower): return 'Yellow'
        elif ('Green' in lower): return 'Green'
        else: 
            return 'Teaware'

    def formatName(self, name):
        return name.lower().replace('yunnan sourcing', '').replace('tea cake', '').replace('ripe', '').replace('raw', '').replace('pu-erh', '')

    def exportString():
        pass

    def __repr__(self):
        return "NAME: {}, VARIANTS: {}".format(self.name, [variant['title'] for variant in self.variants]) + '\n'

PRODUCT_CATALOG = ProductCatalog()

def get_page(url, page, collection_handle):
    print("FETCHING NEW PAGE")
    full_url = url
    if collection_handle:
        full_url += '/collections/{}'.format(collection_handle)
    full_url += '/products.json'
    req = urllib.request.Request(
        full_url + '?limit=250&page={}'.format(page),
        data=None,
        headers={
            'User-Agent': USER_AGENT
        }
    )
    while True:
        try:
            data = urllib.request.urlopen(req).read()
            break
        except HTTPError:
            print('Blocked! Sleeping...')
            time.sleep(180)
            print('Retrying')
        
    products = json.loads(data.decode())['products']
    return products


def get_page_collections(url):
    full_url = url + '/collections.json'
    page = 1
    while page < 5:
        req = urllib.request.Request(
            full_url + '?page={}'.format(page),
            data=None,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        while True:
            try:
                data = urllib.request.urlopen(req).read()
                break
            except HTTPError:
                print('Blocked! Sleeping...')
                time.sleep(180)
                print('Retrying')

        cols = json.loads(data.decode())['collections']
        if not cols:
            break
        for col in cols:
            yield col
        page += 1


def check_shopify(url):
    try:
        get_page(url, 1)
        print('Found shopify!')
        return True
    except Exception:
        return False


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
       not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url

    return fixed_url.rstrip('/')


def getProducts(url):
    extract_products()
    print("Extracting Products Collection...")
    page = 1
    products = get_page(url, page)
    print("PRODUCTS FOR PAGE {}".format(page))
    print([str(product['title']) for product in products])
    while products and page < 10:
        for product in products:
            productObj = YSProduct(product)
            PRODUCT_CATALOG.products.append(productObj)
            print(productObj)

        break
        page += 1
        products = get_page(url, page)

    print("Total Products: " + str(PRODUCT_CATALOG.numProducts()))

def extract_products_collection(url, col):
    page = 1
    products = get_page(url, page, col)
    while products:
        for product in products:
            yield product
            """
            title = product['title']
            product_type = product['product_type']
            product_url = url + '/products/' + product['handle']
            product_handle = product['handle']

            def get_image(variant_id):
                images = product['images']
                for i in images:
                    k = [str(v) for v in i['variant_ids']]
                    if str(variant_id) in k:
                        return i['src']

                return ''

            for i, variant in enumerate(product['variants']):
                price = variant['price']
                option1_value = variant['option1'] or ''
                option2_value = variant['option2'] or ''
                option3_value = variant['option3'] or ''
                option_value = ' '.join([option1_value, option2_value,
                                         option3_value]).strip()
                sku = variant['sku']
                main_image_src = ''
                if product['images']:
                    main_image_src = product['images'][0]['src']

                image_src = get_image(variant['id']) or main_image_src
                stock = 'Yes'
                if not variant['available']:
                    stock = 'No'

                row = {'sku': sku, 'product_type': product_type,
                       'title': title, 'option_value': option_value,
                       'price': price, 'stock': stock, 'body': str(product['body_html']),
                       'variant_id': product_handle + str(variant['id']),
                       'product_url': product_url, 'image_src': image_src}
                for k in row:
                    row[k] = str(row[k].strip()) if row[k] else ''
                yield row
                """
        page += 1
        products = get_page(url, page, col)

def extract_products(url, collections=None):
    seen_variants = set()
    for col in get_page_collections(url):
        if collections and col['handle'] not in collections:
            continue
        handle = col['handle']
        for product in extract_products_collection(url, handle):
            for variant in product['variants']:        
                variant_id = variant['id']
                if variant_id in seen_variants:
                    continue

            seen_variants.add(variant_id)
            productObj = YSProduct(product)
            PRODUCT_CATALOG.products.append(productObj)
            print(productObj)



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--list-collections", dest="list_collections",
                      action="store_true",
                      help="List collections in the site")
    parser.add_option("--collections", "-c", dest="collections",
                      default="",
                      help="Download products only from the given collections (comma separated)")
    (options, args) = parser.parse_args()
    if len(args) > 0:
        url = fix_url(args[0])
        extract_products(url)
        print("TOTAL PRODUCTS: {}".format(PRODUCT_CATALOG.numProducts()))
        PRODUCT_CATALOG.buildCSV()