class Validation:
    @staticmethod
    def validate_product(product):
        if not isinstance(product, dict):
            return False, {'Error':'Invalid Object'}
        
        validation_rules = {
            'title': lambda x: isinstance(x, str),
            'description': lambda x: isinstance(x, str),
            'featured_image': lambda x: isinstance(x, str) and (x.startswith("http://") or x.startswith("https://")),
            'images': lambda x: isinstance(x, list) and all(isinstance(img, str) and (img.startswith("http://") or img.startswith("https://")) for img in x),
            'original_price': lambda x: isinstance(x, (int, float)),
            'sale_price': lambda x: isinstance(x, (int, float))
        }
        
        mandatory_fields = ['id', 'title','link']
        for field in mandatory_fields:
            if field not in product:
                return False, {'Error':field}

        sale_price = product.get('sale_price')
        original_price = product.get('original_price')
        if sale_price is not None and original_price is not None:
            if sale_price > original_price:
                return False, {'Error':'Sale price is higher than Original price'}

        for key, validation_rule in validation_rules.items():
            if key in product:
                if not validation_rule(product[key]):
                    return False, {'Error':key}

        variants = product.get('variants')
        if variants is not None:
            for variant in variants:
                if 'sale_price' not in variant and 'original_price' not in varient:
                    return False, {'Error':key}
                else:
                    if variant['sale_price'] > variant['original_price']:
                        return False, {'Error':'Sale price is higher than Original price'}

        return True,{'Error':''}