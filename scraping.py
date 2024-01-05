from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi
import requests

password = 'Jakmania1928'
cxn_str = f'mongodb+srv://noviansyahh2006:{password}@cluster0.z6ucths.mongodb.net/'
client = MongoClient(cxn_str)
db = client.dbsparta_plus_week13


chrome_options = Options()
chrome_service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=chrome_service)

url = "https://www.yelp.com/search?cflt=restaurants&find_loc=San+Francisco%2C+CA"
driver.get(url)
sleep(3)

driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
sleep(3)

access_token = 'pk.eyJ1IjoibGluY3hsbiIsImEiOiJjbDluMHppMjIwMTR5NDBtejl3NjNueGdyIn0.DLAhnub2hn2okIq0gwCJEw'
long = -122.420679
lat = 37.772537

start = 0
seen = {}

for _ in range(5):
    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    restaurants = soup.select('div[class*="arrange-unit__"]')

    for restaurant in restaurants:
        business_name = restaurant.select_one('div[class*="businessName__"]')
        if not business_name:
            continue

        name = business_name.text.split('.')[-1].strip()

        if name in seen:
            continue

        seen[name] = True

        link = business_name.select_one('a')['href']
        link = 'https://www.yelp.com/' + link

        categories_price_location = restaurant.select_one('div[class*="priceCategory__"]')
        spans = categories_price_location.select('span')
        categories = spans[0].text
        location = spans[-1].text

        geo_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?proximity={long},{lat}&access_token={access_token}"
        geo_response = requests.get(geo_url)
        geo_json = geo_response.json()
        center = geo_json['features'][0]['center']
        print(name, categories, location, center)
        doc = {
            'name': name,
            'categories': categories,
            'location': location,
            'link' : link,
            'center': center,
        }

        print(name, ',', categories, ',', location, ',', link)
        db.restaurants.insert_one(doc)

    start += 10
    driver.get(f'{url}&start={start}')
    sleep(3)

driver.quit()