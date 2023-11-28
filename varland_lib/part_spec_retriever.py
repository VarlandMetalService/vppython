import requests

class PartSpecRetriever:
    
    @classmethod
    def get(cls, shop_order):
      url = 'http://json400.varland.com/part_spec_for_shop_order'
      params = { 'shop_order': shop_order }
      response = requests.get(url, params=params)
      if response.status_code == 200:
        data = response.json()
        return (data['part_spec'] if data['valid_order'] else "")
      else:
        return ""