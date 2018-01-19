from .contract import ExchangeClient, Asset, AssetException
import json
from .meta import exchange_api, quotation_provicer


@exchange_api('BackTest', configs=[
    {
        'name': 'init_assets',
        'description': '初始资产',
        'type': 'string',
        'required': False
    }
])
class BackTestClient(ExchangeClient):
    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=True, indent=2)

    def __init__(self, exchange, assets={}):
        self.exchange = exchange
        self.assets = {}
        self.traders = []
        for x in assets.keys():
            self.assets[x] = Asset(x, assets[x])

    def get_assets(self):
        '''
        交易所对象
        '''
        return self.assets

    def buy(self, symbol, price, volume, type_=None):
        [bsym, ssym] = symbol.split('/')
        print(bsym, ssym)
        amount = round(price * volume, 8)
        if ssym not in self.assets or self.assets[ssym].balance < amount:

            raise AssetException('资产不足', ssym)
        self.assets[ssym].balance = self.assets[ssym].balance - amount
        self.assets[bsym].balance = self.assets[bsym].balance + volume

    def sell(self, symbol, price, volume, type_=None):
        [ssym, bsym] = symbol.split('/')
        amount = round(price * volume, 8)
        if ssym not in self.assets or self.assets[ssym].balance < amount:
            raise AssetException('资产不足', self.assets[ssym])
        self.assets[ssym].balance = self.assets[ssym].balance - amount
        self.assets[bsym].balance = self.assets[bsym].balance + volume

    def cancel_order(self, order_id):
        pass

    def get_order(self, order_id):
        pass
