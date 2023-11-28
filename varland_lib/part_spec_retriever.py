import requests
from pycomm3 import LogixDriver

class PartSpecRetriever:
    
    @classmethod
    def calc_variable_name(cls, shop_order_tag):
      variable = shop_order_tag.split('.')[-1]
      prefix = variable.split('_')[0]
      return shop_order_tag.replace(prefix, 's').replace('_ShopOrder', '_PartSpec')
    
    @classmethod
    def get(cls, shop_order, shop_order_tag, cfg):
      part_spec_tag = cls.calc_variable_name(shop_order_tag)
      part_spec = ""
      if int(shop_order) != 0:
        url = 'http://json400.varland.com/part_spec_for_shop_order'
        params = { 'shop_order': shop_order }
        response = requests.get(url, params=params)
        if response.status_code == 200:
          data = response.json()
          part_spec = (data['part_spec'] if data['valid_order'] else "")
      with LogixDriver(cfg.get('en_controller_ip')) as plc:
        plc.write((part_spec_tag, part_spec))