import csv
from time import sleep

seenIds = []
toadd = []
caught = 0
iterated = 0
catalog_len_ndupes = 0

with open('products.csv', 'r', encoding="utf-8") as r:
    read = csv.reader(r)
    for line in read:
        iterated += 1
        if (iterated == 0): 
            print('Skipping First Line')
            sleep(3)
            iterated += 1
            continue
        if (line == []):
            continue
        if (line[-1] in seenIds):
            print('Found Dupe!')
            caught += 1
            continue
        else:
            print(line)
            seenIds.append(line[-1])
            toadd.append(line)
            catalog_len_ndupes += 1

with open('products_no_dupes.csv', 'w', newline="", encoding="utf-8") as w:
    writer = csv.writer(w)
    print('Out CSV Inited. Adding Rows..')
    for row in toadd:
        writer.writerow(row)

print("Processed {} items, found {} duplicates, for new len of {}"
    .format(iterated, caught, catalog_len_ndupes))