from contextlib import nullcontext
from selenium import webdriver
from os import access
import pandas
import requests
import json
from time import sleep, strftime
from requests.structures import CaseInsensitiveDict

region='eu'
langue='fr'
locale='fr_EU'
realm='1127'

def get_token():
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Authorization"] = "Basic MGRmN2FkNDBhZDVmNDdkYzg5MjdjZmVkNDc5NWVmZDU6ZHVOMXdoYWd3ekhMcnZYSkwzajVRRW9kQkljdVZkbWM="

    url_token='https://us.battle.net/oauth/token'
    data = "grant_type=client_credentials"

    res = requests.post(url_token, data=data, headers=headers)

    token_json = json.loads(res.text)
    access_token = token_json["access_token"]

    return access_token

#### ENVRIONMENT

headersWithToken = {
    'Authorization': 'Bearer '+str(get_token()),
    'Content-Type': 'application/json;charset=UTF-8'
}

paramsStatic = (
    ('namespace', 'static-'+region),
    ('locale', locale)
)

paramsDynamic = (
    ('namespace', 'dynamic-'+region),
    ('locale', locale)
)

#### END ENVRIONMENT

def divid_money(price):
    gold = price/10000
    price = price%10000
    silver = price/100
    copper = price%100

    money=str(gold)+"Or "+str(silver)+"Argent "+str(copper)+"Bronze"

    return money

def get_icon_item(id_item):
    url_item='https://'+region+'.api.blizzard.com/data/wow/media/item/'

    response = requests.get(url_item+str(id_item), headers=headersWithToken, params=paramsStatic)
    data = json.loads(response.text)

    itemAsset = data["assets"]
    #itemImage = itemAsset["value"]
    for asset in itemAsset:
        itemImage = asset["value"]

    return itemImage

def get_all_auctions_form():
    url_auctions='https://'+region+'.api.blizzard.com/data/wow/connected-realm/'+realm+'/auctions'

    response = requests.get(url_auctions, headers=headersWithToken, params=paramsDynamic)
    data = json.loads(response.text)

    auctions = data["auctions"]

    for auction in auctions:
        if "buyout" in auction:
            price = auction['buyout']
    
        if "unit_price" in auction:
            price = auction['unit_price']

        id_item = auction['item']['id']
        quantity = auction['quantity']
        time_left = auction['time_left']
        price = divid_money(price)

        print("Item: "+str(id_item)+", Quantité: "+str(quantity)+", Temps restant: "+str(time_left)+", Prix: "+str(price))

def get_all_auctions_json():
    url_auctions='https://'+region+'.api.blizzard.com/data/wow/connected-realm/'+realm+'/auctions'

    response = requests.get(url_auctions, headers=headersWithToken, params=paramsDynamic)
    data = json.loads(response.text)

    auctions = data["auctions"]

    for auction in auctions:
        if "buyout" in auction:
            price = auction['buyout']
    
        if "unit_price" in auction:
            price = auction['unit_price']

        id_item = auction['item']['id']
        quantity = auction['quantity']
        time_left = auction['time_left']
        price = divid_money(price)

        auction = [id_item, quantity, time_left, price]

        print(json.dumps(auction))

def get_one_auction(name_item):

    url_auctions='https://'+region+'.api.blizzard.com/data/wow/connected-realm/'+realm+'/auctions'

    response = requests.get(url_auctions, headers=headersWithToken, params=paramsDynamic)
    data = json.loads(response.text)

    auctions = data["auctions"]
    
    item = get_inf_item(name_item)
    itemA = None
    lower_price = 99999999999

    for auction in auctions:
        id_item = auction['item']['id']

        if str(auction['item']['id']) == str(item["id"]):
            itemA = auction

            if "buyout" in itemA:
                price = itemA['buyout']

            if "unit_price" in itemA:
                price = itemA['unit_price']

            name_item = item["name"]["fr_FR"]
            quantity = itemA['quantity']
            time_left = itemA['time_left']
            image = get_icon_item(str(id_item))

            ###for each auction get the auction with the lowest price
            if price < lower_price:
                lower_price = price
                lower_action = itemA

            if price == lower_price:
                ###put in json file
                json_convert = {
                    'auctions' : [
                        {
                            'image' : image,
                            'name' : str(item["name"]["fr_FR"]),
                            'quantity' : str(lower_action['quantity']),
                            'time_left' : str(lower_action['time_left']),
                            'price' : str(price)
                        }
                    ]
                }

                ###don't delete old json
                write_in_jsonfile(json_convert)

            price = divid_money(price)
            print(image+" Nom: "+str(name_item)+", Quantité: "+str(quantity)+", Temps restant: "+str(time_left)+", Prix: "+str(price))

    if itemA is None:
        print("Aucun de ces object n'est en vente actuellement")

def get_inf_item(name_item):
    url_auctions='https://'+region+'.api.blizzard.com/data/wow/search/item'

    params = (
        ('namespace', 'static-'+region),
        ('locale', locale),
        ('name.en_US', str(name_item)),
        ('orderby', 'id'),
        ('_page', '1')
    )

    response = requests.get(url_auctions, headers=headersWithToken, params=params)
    data = json.loads(response.text)

    items = data["results"]

    for item in items:
        theItemData = item["data"]
        if str(name_item) == str(theItemData["name"]["fr_FR"]):
            theItem = theItemData

    return theItem

def show_auction_in_browser(name_item):
    try:
        lines = get_one_auction(name_item)
        driver = webdriver.Chrome()
        driver.get("./index.html")
        elm = driver.find_element_by_id("ventes")
        driver.execute_script("arguments[0].innerHTML = '"+lines+"';", elm)
        sleep(10)
    
    finally:
        # Closing the webdriver
        driver.close()

def write_in_jsonfile(data):
    with open('auctions.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)

get_one_auction("Machine volante")
#show_auction_in_browser("Machine volante")