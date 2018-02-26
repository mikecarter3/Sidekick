###################################################################
#   This is a batch conversion file that takes an input wix csv   #
#   order file and outputs a tab-delimited txt file formatted     #
#   for uploading directly to amazon FBA.                         #
#                                                                 #
#   Developed by: Mike Carter                                     #
#   Property of: Renegade Innovations, LLC                        #
#   Written: 2018-02-19                                           #
###################################################################

import argparse
import csv
import datetime

def parse_args():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--from", type=str, required=True, default="none",
                    help="path to input Wix csv batch file")
    args = vars(ap.parse_args())
    return args

def check_order_fields(order):
    fields_are_valid = True
    if order['notes2seller']:
        print('\nATTENTION: SPECIAL INSTRUCTIONS ON ORDER ', order['MerchantFulfillmentOrderID'],': \n\n',
              order['notes2seller'], '\n')
    for key in order.keys():
        #print(key, order[key])
        if key is 'notes2seller': continue
        if not order[key]:
            fields_are_valid = False
            print('Order ', order['MerchantFulfillmentOrderID'], 'is missing field: ', key)
    return fields_are_valid

def read_wix_csv(filename):
    orders = []
    with open(filename, mode='r') as wix_csv:
        reader = csv.DictReader(wix_csv, )
        for row in reader:
            #print(row)
            order = {'MerchantFulfillmentOrderID': row['Order #'],
                     'date': row['Date'],
                     'time': row['Time'],
                     'MerchantSKU': row['SKU'],
                     'Quantity': row['Qty'],
                     'AddressName': row['Delivery Customer'],
                     'AddressFieldOne': row['Delivery Street Name&Number'],
                     'AddressCity': row['Delivery City'],
                     'AddressStateOrRegion': row['Delivery State'],
                     'AddressPostalCode': row['Delivery Zip Code'],
                     'AddressPhoneNumber': row['Buyer\'s Phone #'],
                     'NotificationEmail': row['Buyer\'s Email'],
                     'notes2seller': row['Notes to Seller'],
                     }
            if check_order_fields(order):
                orders.append(order)
    return orders

## Not complete
def add_amazon_fields(orders):
    batch_index = 0
    for order in orders:
        batch_index+=1
        order['DisplayableOrderID'] = order['MerchantFulfillmentOrderID']
        date = datetime.datetime.strptime(order['date']+' '+order['time'], "%b %d, %Y %I:%M:%S %p")
        order['DisplayableOrderDate'] = date.isoformat()
        order['MerchantFulfillmentOrderItemID'] = str(batch_index)
        order['GiftMessage'] = ''
        order['DisplayableComment'] = ''
        order['PerUnitDeclaredValue'] = ''
        order['DisplayableOrderComment'] = 'Thank you for your order!'
        order['DeliverySLA'] = 'Standard'
        order['AddressFieldTwo'] = ''
        order['AddressFieldThree'] = ''
        order['AddressCountryCode'] = 'US' # NOTE THIS IS HARD CODED FOR THE USA
        order['AddressStateOrRegion'] = order['AddressStateOrRegion'][3:]
        order['AddressPostalCode'] = order['AddressPostalCode'][1:6]
        order['FulfillmentAction'] = 'Ship'
        order['AddressPhoneNumber'] = '' # For now we're not including phone number (it's optional)
        order['MarketplaceID'] = ''
    return orders

def write_amazon_csv(orders):
    field_names = ['MerchantFulfillmentOrderID','DisplayableOrderID',
                   'DisplayableOrderDate','MerchantSKU','Quantity',
                   'MerchantFulfillmentOrderItemID','GiftMessage',
                   'DisplayableComment','PerUnitDeclaredValue',
                   'DisplayableOrderComment','DeliverySLA','AddressName',
                   'AddressFieldOne','AddressFieldTwo','AddressFieldThree',
                   'AddressCity','AddressCountryCode','AddressStateOrRegion',
                   'AddressPostalCode','AddressPhoneNumber','NotificationEmail',
                   'FulfillmentAction','MarketplaceID']
    filename = 'amazon_formatted/'+in_filename+'.csv'
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(orders)

### Read orders from wix csv file
args = parse_args()
in_filename = args['from']
order_data = read_wix_csv(in_filename)

### Create new fields for amazon file
order_data = add_amazon_fields(order_data)

### Save amazon formatted file
write_amazon_csv(order_data)