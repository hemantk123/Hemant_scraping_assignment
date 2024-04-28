import time
import json
import math
import requests
from random import randint
from parsel import Selector
from bs4 import BeautifulSoup
from selenium import webdriver
from w3lib.html import remove_tags
from validation import Validation


base_url = 'https://www.traderjoes.com/home/products/category/products-2'

def complete_relative_url(url, base_url='https://www.traderjoes.com'):
    if base_url not in url:
        url = f'{base_url}{url}'
    return url

data = []

base_api_url = 'https://www.traderjoes.com/api/graphql'
pageSize = 100
payload = {'query': 'query SearchProducts($categoryId: String, $currentPage: Int, $pageSize: Int, $storeCode: String = "TJ", $published: String = "1") {\n  products(\n    filter: {store_code: {eq: $storeCode}, published: {eq: $published}, category_id: {eq: $categoryId}}\n    currentPage: $currentPage\n    pageSize: $pageSize\n  ) {\n    items {\n      sku\n      availability\n      item_title\n      category_hierarchy {\n        id\n        name\n        __typename\n      }\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      sales_size\n      sales_uom_description\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      fun_tags\n      item_characteristics\n      __typename\n    }\n    total_count\n    pageInfo: page_info {\n      currentPage: current_page\n      totalPages: total_pages\n      __typename\n    }\n    aggregations {\n      attribute_code\n      label\n      count\n      options {\n        label\n        value\n        count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n', 'variables': {'storeCode': 'TJ', 'availability': '1', 'published': '1', 'categoryId': 2, 'currentPage': 1, 'pageSize': pageSize}}

headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

response = requests.request("POST", base_api_url, headers=headers, data=json.dumps(payload))

data_for_total_products = response.json()
total_products = data_for_total_products['data']['products']['total_count']
pages = math.ceil(total_products/pageSize)


for page in range(pages):
    payload['variables']['currentPage'] = page + 1 
    response = requests.request("POST", base_api_url, headers=headers, data=json.dumps(payload))
    time.sleep(randint(2,5))
    products = response.json()['data']['products']['items']
    for indd,product in enumerate(products):
        product_data = {}

        product_data['id'] = product['sku']

        product_data['title'] = product['item_title']
        product_data['link'] = f"https://www.traderjoes.com/home/products/pdp/{product['item_title'].strip().lower().replace(' ','-')}-{product_data['id']}"

        product_data['weight'] = f"{str(product['sales_size'])}{product['sales_uom_description']}"

        product_data['featured_image'] = complete_relative_url(product['primary_image'])
        product_data['images'] = [ product_data['featured_image']]

        product_data['sale_price'] = float(product['price_range']['minimum_price']['final_price']['value'])
        product_data['original_price'] = float(product['retail_price'])
        product_data['price_currency'] = product['price_range']['minimum_price']['final_price']['currency']

        product_data['item_characteristics'] = product.get('item_characteristics') if product.get('item_characteristics') else None

        product_data['available'] = True if product['availability'] == '1' else False

        in_payload = {'query': 'query SearchProduct($sku: String, $storeCode: String = "TJ", $published: String = "1") {\n  products(\n    filter: {sku: {eq: $sku}, store_code: {eq: $storeCode}, published: {eq: $published}}\n  ) {\n    items {\n      category_hierarchy {\n        id\n        url_key\n        description\n        name\n        position\n        level\n        created_at\n        updated_at\n        product_count\n        __typename\n      }\n      item_story_marketing\n      product_label\n      fun_tags\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      other_images\n      other_images_meta {\n        url\n        metadata\n        __typename\n      }\n      context_image\n      context_image_meta {\n        url\n        metadata\n        __typename\n      }\n      published\n      sku\n      url_key\n      name\n      item_description\n      item_title\n      item_characteristics\n      item_story_qil\n      use_and_demo\n      sales_size\n      sales_uom_code\n      sales_uom_description\n      country_of_origin\n      availability\n      new_product\n      promotion\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      nutrition {\n        display_sequence\n        panel_id\n        panel_title\n        serving_size\n        calories_per_serving\n        servings_per_container\n        details {\n          display_seq\n          nutritional_item\n          amount\n          percent_dv\n          __typename\n        }\n        __typename\n      }\n      ingredients {\n        display_sequence\n        ingredient\n        __typename\n      }\n      allergens {\n        display_sequence\n        ingredient\n        __typename\n      }\n      created_at\n      first_published_date\n      last_published_date\n      updated_at\n      related_products {\n        sku\n        item_title\n        primary_image\n        primary_image_meta {\n          url\n          metadata\n          __typename\n        }\n        price_range {\n          minimum_price {\n            final_price {\n              currency\n              value\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        retail_price\n        sales_size\n        sales_uom_description\n        category_hierarchy {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    total_count\n    page_info {\n      current_page\n      page_size\n      total_pages\n      __typename\n    }\n    __typename\n  }\n}\n', 'variables': {'storeCode': 'TJ', 'published': '1', 'sku': product_data['id']}}
        response = requests.request("POST", base_api_url, headers=headers, data=json.dumps(in_payload))
        time.sleep(randint(2,5))
        product_info = response.json()['data']['products']['items'][0]

        product_data['description'] = remove_tags(product_info['item_story_marketing']) if product_info.get('item_story_marketing') else None

        product_data['images'].append(complete_relative_url(product_info['context_image'])) if product_info.get('context_image') else None

        if product_info.get('nutrition'):
            product_data['nutrition'] = {   'serving_size':product_info['nutrition'][0]['serving_size'],
                                            'calories_per_serving':product_info['nutrition'][0]['calories_per_serving'],
                                            'servings_per_container':product_info['nutrition'][0]['servings_per_container'],
                                            'details':[{k: v for k, v in item.items() if k not in ['display_seq', '__typename']} for item in product_info['nutrition'][0]['details']]
                                            }
        if product_info.get('ingredients'):
            product_data['ingredients'] = [ i['ingredient'] for i in product_info['ingredients'] ]

        product_data['page'] = page + 1

        print(Validation.validate_product(product_data)) #No hard check on this some products dont have product_id(id) which is one of mandatory fields

data.append(product_data)

out_file = open("../output/traderjoes.json", "w")

json.dump({'data':data}, out_file, indent = 6) 
out_file.close() 
