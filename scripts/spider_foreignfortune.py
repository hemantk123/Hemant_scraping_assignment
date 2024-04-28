import time
import json
import requests
from random import randint
from parsel import Selector
from selenium import webdriver
from validation import Validation

base_url = 'https://foreignfortune.com'

def complete_relative_url(url, base_url=base_url):
    if base_url not in url:
        url = f'{base_url}{url}'
    return url


driver = webdriver.Chrome()
response = driver.get(base_url)
time.sleep(randint(2,5))
data = []

selector = Selector(text=driver.page_source)
nav_bar_categories = selector.xpath('//nav[@id="AccessibleNav"]//li')
for nav_bar_category in nav_bar_categories:
    temp = {}
    nav_bar_category_link_raw = nav_bar_category.xpath('.//a/@href').get()
    nav_bar_category_link = complete_relative_url(nav_bar_category_link_raw)
    nav_bar_category_name = nav_bar_category.xpath('.//a/text()').get()
    temp['section'] = nav_bar_category_name.strip()
    temp['link'] = nav_bar_category_link.strip()
    temp['products'] = []

    driver.get(nav_bar_category_link)
    time.sleep(randint(2,5))
    selector = Selector(text=driver.page_source)

    pages = selector.xpath('//div[@id="Collection"]//li[@class="pagination__text"]/text()').get()
    if pages:
        pages = int(pages.split('of')[1])
    else:
        pages = 1
    for page in range(pages):

        driver.get(f'{nav_bar_category_link}?page={page+1}')
        time.sleep(randint(2,5))
        selector = Selector(text=driver.page_source)

        products = selector.xpath('//div[@id="Collection"]//div[contains(@class,"product-card")]')
        for product in products:
            product_data = {}

            product_link_raw = product.xpath('.//a/@href').get()
            product_link = complete_relative_url(product_link_raw)

            driver.get(product_link)
            time.sleep(randint(2,5))
            selector = Selector(text=driver.page_source)

            test = selector.xpath('//*[@id="ProductJson-product-template"]/text()').get()
            temp_data = json.loads(test)

            product_data['id'] = temp_data['id']
            product_data['title'] = temp_data['title']
            product_data['description'] = temp_data['description']
            product_data['link'] = product_link

            product_data['featured_image'] = f'https:{temp_data["featured_image"]}' if 'https:' not in temp_data['featured_image'] else temp_data['featured_image']
            product_data['images'] = [ f'https:{img_link}' if 'https:' not in img_link else img_link for img_link in temp_data['images']]

            product_data['page'] = page + 1

            product_data['varients'] = []
            product_data['vendor'] = temp_data['vendor']

            for varient in temp_data['variants']:
                varient_temp = {}

                varient_temp['id'] = varient['id']
                varient_temp['available'] = varient['available']

                varient_temp.update(dict(zip([i.lower() for i in temp_data['options']],varient['options'])))

                varient_temp['sale_price'] = float(varient['price'])/100
                varient_temp['original_price'] = varient_temp['sale_price']
                product_data['varients'].append(varient_temp)

            print(Validation.validate_product(product_data)) #No hard check on this some products dont have product_id(id) which is one of mandatory fields

            temp['products'].append(product_data)
    data.append(temp)

out_file = open("../output/foreignfortune.json", "w")

json.dump({'data':data}, out_file, indent = 6) 
out_file.close() 

driver.quit()