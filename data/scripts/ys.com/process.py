import json
import csv
import time
import os
import ast

"""
Json Schema
{
    id,
    name,
    type_standard, str from [oolong, sheng, shou, white, black, green, yellow]
    type, type from catalog
    prices, ARRAY of all prices for item incliuding variants
    quantities, ARRAY of all quantities for item including variants
    url, str
    image_url, str
    tags, array,
    ppg
}
"""
COLLECTION_INDEX = 0
TYPE_INDEX = 1
NAME_INDEX = 2
VARIANT_NAME_INDEX = 3
PRICE_INDEX = 4
URL_INDEX = 5
ID_INDEX = 6
TAGS_INDEX = 7
IMAGES_INDEX = 8
ORIGIN_VENDOR_INDEX = 9
QUANTITY_OPTIONS_INDEX = 10

inData = []
seenIds = []
outData = []

def standardizeCataegory(nonStandard):
    lower = nonStandard.lower()
    if ('ripe' in lower): return 'Shou'
    elif ('raw' in lower): return 'Sheng'
    elif ('oolong' in lower): return 'Oolong'
    elif ('black' in lower): return 'Black'
    elif ('white' in lower): return 'White'
    elif ('yellow' in lower): return 'Yellow'
    elif ('Green' in lower): return 'Green'
    else: 
        return None

def checkForVariant(id, index):
    """Checks to see if there is a product variant on the next line"""
    try:
        if (inData[index + 1][-2] == id):
            print('Variant found for id {}'.format(id))
            return True
        else:
            print('Variant not found for id {}'.format(id))
            return False
    except IndexError:
        return False

def findNVariants(id, index, n):
    """Returns the total number of variants of a product, assuming they are consecutive in the data"""
    try:
        if (inData[index][-2] != id):
            return n
        else:
            return findNVariants(id, index + 1, n + 1)
    except IndexError:
        return n

def extractYear(tags, name):
    for tag in tags:
        if (tag.isnumeric() and int(tag) > 1900 and int(tag) < 3000):
            return int(tag)

    for item in name.split(' '):
        if (item.isnumeric() and int(item) > 1900 and int(item) < 3000):
            return int(item)

    return None

def extractSeason(tags):
    seasons = ['autumn', 'fall', 'spring', 'summer', 'winter']

    for tag in tags:
        if 'Harvest' in tag:
            return tag.split(' ')[0]
        elif any(season in tag.lower() for season in seasons):
            for season in seasons:
                if season in tag:
                    return season
        else:
            return None

def extractForm(variantName):
    lower = variantName.lower()
    if ('cake' in lower):
        return 'cake'
    elif ('brick' in lower):
        return 'brick'
    elif ('ball' in lower):
        return 'ball'
    elif ('sample' in lower):
        return 'sample'
    else:
        return None

def extractWeigt(fullVariantName):
    """
        Picks the weight of a product variant out of the variant name
        returns the found variant weight in grams    
    """
    lower = fullVariantName.lower()
    nameNoParens = lower.replace('(', '').replace(')', '')
    splitNameNoParens = nameNoParens.split(' ')
    try:
        # Yes, I know this is ugly, and I know there's a better way, but I just don't care right now :)
        if 'grams' in lower: # if contains "grams" get number right before
            i = splitNameNoParens.index('grams')
            return int(splitNameNoParens[i - 1])
        elif 'gram' in lower:
            i = splitNameNoParens.index('gram')
            return int(splitNameNoParens[i - 1])
        elif 'kilogram' in lower:
            i = splitNameNoParens.index('kilogram')
            return int(splitNameNoParens[i - 1] * 1000)
        elif 'kilograms' in lower:
            i = splitNameNoParens.index('kilograms')
            return int(splitNameNoParens[i - 1] * 1000)
        elif 'ball' in lower:
            i = splitNameNoParens.index('ball')
            return int(splitNameNoParens[i - 1])
        elif 'balls' in lower:
            i = splitNameNoParens.index('balls')
            return int(splitNameNoParens[i - 1])
        elif 'tong' in lower:
            i = splitNameNoParens.index('tong')
            return int(splitNameNoParens[i - 1])
        else:
            print("UNKOWN WEIGHT FORMAT: {}".format(fullVariantName))
            return 
    except:
        return -1

def genPPG(prices, weights):
    """
        Generates low and high price per gram amounts for an item
        returns an array, with first element being low, and second element being high
            if there is only one variant of an item, a single element array will be returned
    """
    try:
        assert(prices is not None and weights is not None)
        print("PRICES: {}, WEIGHTS: {}".format(prices, weights))
        if len(prices) == 1 and len(weights) == 1:
            return round(float(prices[0]) / float(weights[0]), 2)
        else:
            return [
                round(float(min(prices)) / float(min(weights)), 2),
                round(float(max(prices)) / float(max(weights)), 2)
            ]
    except TypeError:
        return None
    except AssertionError as e:
        print("AssertionError Caught in genPPG")
        return []

def exportJSON():
    wrapped = { 'products': outData }
    with open('ys-catalog5.json', 'w', encoding="utf-8") as out:
        json.dump(wrapped, out)

if __name__ == '__main__':
    rowIndex = 1
    addedIds = []
    with open('products-30lim.csv', 'r', encoding="utf-8") as fin:
        inData = [line for line in csv.reader(fin) if line != []]    

    while rowIndex < len(inData):
        row = inData[rowIndex]
        tags = ast.literal_eval(row[TAGS_INDEX])
        images = ast.literal_eval(row[IMAGES_INDEX])
        item = {
            'id': row[ID_INDEX],
            'name': row[NAME_INDEX],
            'type': standardizeCataegory(row[TYPE_INDEX]),
            'type_nonstandard': row[TYPE_INDEX],
            'url': row[URL_INDEX],
            'images': images,
            'tags': tags,
            'sample_available': 'Sample Available' in tags,
            'year': extractYear(tags, row[NAME_INDEX]),
            'season': extractSeason(tags),
            'variants': []
        }

        if (row[ID_INDEX] in seenIds): # if we've already seen this product id
            for product in outData:
                if product['id'] == row[ID_INDEX]: # find product entry in outdata
                    try:
                        if (isinstance(product['prices'], str) or isinstance(product['prices'], int) or isinstance(product['prices'], float)):
                            product['prices'] = [product['prices'], row[PRICE_INDEX]]
                        else:
                            product['prices'].append(row[PRICE_INDEX])
                    except KeyError:
                        product['prices'] = row[PRICE_INDEX]

                    try:
                        if (isinstance(product['quantities'], str) or isinstance(product['quantities'], int) or isinstance(product['quantities'], float)):
                            product['quantities'] = [product['quantities'], extractWeigt(row[VARIANT_NAME_INDEX])]
                        else:
                            product['quantities'].append(extractWeigt(row[VARIANT_NAME_INDEX]))
                    except KeyError:
                        product['quantities'] = extractWeigt(row[VARIANT_NAME_INDEX])
                    except AttributeError:
                        product['quantities'] = None

                    try:
                        if (isinstance(product['ppg'], str) or isinstance(product['ppg'], int) or isinstance(product['ppg'], float)):
                            product['ppg'] = [product['ppg'], genPPG([row[PRICE_INDEX]], [extractWeigt(row[VARIANT_NAME_INDEX])])]
                        else:
                            product['ppg'].append(genPPG([row[PRICE_INDEX]], [extractWeigt(row[VARIANT_NAME_INDEX])]))
                    except KeyError:
                        product['ppg'] = genPPG([row[PRICE_INDEX]], [extractWeigt(row[VARIANT_NAME_INDEX])])
                    except AttributeError:
                        product['ppg'] = None

                    product['variants'].append(
                        {
                            'name': row[VARIANT_NAME_INDEX],
                            'price': row[PRICE_INDEX],
                            'quantity': extractWeigt(row[VARIANT_NAME_INDEX]),
                            'form': extractForm(row[VARIANT_NAME_INDEX])
                        }
                    )
        else: #if new product
            item['prices'] = row[PRICE_INDEX]
            item['quantities'] = extractWeigt(row[VARIANT_NAME_INDEX])
            item['ppg'] = genPPG([row[PRICE_INDEX]], [extractWeigt(row[VARIANT_NAME_INDEX])])
            item['variants'].append(
                {
                    'name': row[VARIANT_NAME_INDEX],
                    'price': row[PRICE_INDEX],
                    'quantity': extractWeigt(row[VARIANT_NAME_INDEX]),
                    'form': extractForm(row[VARIANT_NAME_INDEX])
                }
            )


        """
        if (checkForVariant(row[ID_INDEX], rowIndex)): # If there is a variant of the current product
            prices = []
            quantities = []

            totalNProductVariants = findNVariants(row[ID_INDEX], rowIndex, 0)
            for rowI in range(rowIndex, rowIndex + totalNProductVariants):
                item['variants'].append(
                    {
                        'name': inData[rowI][VARIANT_NAME_INDEX],
                        'price': inData[rowI][PRICE_INDEX],
                        'quantity': extractWeigt(inData[rowI][VARIANT_NAME_INDEX]),
                        'form': extractForm(inData[rowI][VARIANT_NAME_INDEX])
                    }
                )
                prices.append(inData[rowI][PRICE_INDEX])
                quantities.append(extractWeigt(inData[rowI][VARIANT_NAME_INDEX]))
            
            item['prices'] = prices
            item['quantities'] = quantities
            item['ppg'] = genPPG(prices, quantities)
        else:
            item['prices'] = [row[PRICE_INDEX]]
            item['quantities'] = extractWeigt(row[VARIANT_NAME_INDEX])
            item['ppg'] = genPPG([row[PRICE_INDEX]], [extractWeigt(row[VARIANT_NAME_INDEX])])
            item['variants'].append(
            {
                'name': row[VARIANT_NAME_INDEX],
                'price': row[PRICE_INDEX],
                'quantity': extractWeigt(row[VARIANT_NAME_INDEX]),
                'form': extractForm(row[VARIANT_NAME_INDEX])
            })
            """

        seenIds.append(row[ID_INDEX])
        outData.append(item)


        #if checkForVariant(row[ID_INDEX], rowIndex):
         #   rowIndex += totalNProductVariants
        #else:
         #   rowIndex += 1
        rowIndex += 1

    #print("OUTPUT:")
    #for i in outData:
     #   print(i)
    
    exportJSON()
    print("JSON Exported.")
