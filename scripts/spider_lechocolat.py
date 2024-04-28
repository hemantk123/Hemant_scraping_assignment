import time
import json
import requests
from random import randint
from parsel import Selector
from bs4 import BeautifulSoup
from selenium import webdriver
from validation import Validation


base_url = 'https://www.lechocolat-alainducasse.com/uk/'

def complete_relative_url(url, base_url=base_url):
    if base_url not in url:
        url = f'{base_url.split("/uk/")[0]}{url}'
    return url


driver = webdriver.Chrome()
response = driver.get(base_url)
time.sleep(randint(2,5))
data = []

selector = Selector(text=driver.page_source)
nav_bar_categories = selector.xpath('//section[@class="homeCategoryPads"]//li')
for nav_bar_category in nav_bar_categories:
    temp = {}
    nav_bar_category_link_raw = nav_bar_category.xpath('.//a/@href').get()
    nav_bar_category_link = complete_relative_url(nav_bar_category_link_raw)
    nav_bar_category_names = [i.strip() for i in nav_bar_category.xpath('.//p/text()').getall()]
    nav_bar_category_name = ''.join([f' {i.strip()}' if i[0].isupper() else i.strip() for i in nav_bar_category_names])
    temp['section'] = nav_bar_category_name.strip()
    temp['link'] = nav_bar_category_link.strip()
    temp['products'] = []

    driver.get(nav_bar_category_link)
    time.sleep(randint(2,5))
    selector = Selector(text=driver.page_source)

    products = selector.xpath('//section[@id="js-product-list"]//section[contains(@class,"productMiniature__data")]')
    for product in products:
        product_data = {}

        product_link_raw = product.xpath('.//a/@href').get()
        product_link = complete_relative_url(product_link_raw)

        driver.get(product_link)
        time.sleep(randint(2,5))
        selector = Selector(text=driver.page_source)

        test = selector.xpath('//main[@id="main"]//script[@type="application/ld+json"]/text()').get()
        temp_data = json.loads(test)

        if temp_data.get('sku'):
            product_data['id'] = temp_data['sku']
        product_data['title'] = temp_data['name']
        title_small = selector.xpath('//div[@class="productCard"]//h1[@class="productCard__title"]/small/text()').get()
        if title_small:
            product_data['title_small'] = title_small.strip()
        subtitle = selector.xpath('//div[@class="productCard"]//h2[@class="productCard__subtitle"]/text()').get()
        if subtitle:
            product_data['subtitle'] = subtitle.strip()
        weight = selector.xpath('//div[@class="productCard"]//p[@class="productCard__weight"]/text()').get()
        if weight:
            product_data['weight'] = weight.strip()

        consume_advice = selector.xpath('//div[@class="productCard"]//div[@class="productDescription"]//p[@class="consumeAdvices"]/strong/text()').get()
        if consume_advice:
            product_data['consume_advice'] = consume_advice.strip()

        if temp_data.get('description'):
            product_data['description'] = temp_data['description']
        product_data['link'] = product_link

        product_data['featured_image'] = f'https:{temp_data["image"]}' if 'https:' not in temp_data['image'] else temp_data['image']
        product_data['images'] = [ product_data['featured_image']]

        product_data['sale_price'] = float(temp_data['offers']['price'])
        product_data['original_price'] = float(temp_data['offers']['price'])
        product_data['price_currency'] = temp_data['offers']['priceCurrency']

        product_data['consume_advice'] = selector.xpath('//div[@class="productCard"]//div[@class="productDescription"]//p[@class="consumeAdvices"]/strong/text()').get().strip()

        availability = selector.xpath('//main[@id="main"]//div[@class="product-additional-info"]//p[@class="mailAlert__message"]/strong/text()').get()
        product_data['available'] = False if availability and 'unavailable' in availability else True

        product_infos = selector.xpath('//details[@id="product_tab_informations"]//h3[@class="wysiwyg-title-default"]')
        for product_info in product_infos:
            heading = product_info.xpath('./text()').get().strip()
            message = product_info.xpath('./following-sibling::p/text()').get().strip()
            product_data[heading] = message


        print(Validation.validate_product(product_data)) #No hard check on this some products dont have product_id(id) which is one of mandatory fields

        temp['products'].append(product_data)
    data.append(temp)

out_file = open("../output/lechocolat.json", "w")

json.dump({'data':data}, out_file, indent = 6) 
out_file.close() 

driver.quit()