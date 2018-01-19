from abc import abstractclassmethod
import json
import time


class QuotationClient:

    @abstractclassmethod
    def get_exchange_symbols(self):
        """查询当前交易所支持的所有交易对
        :return:
            {
            "raw": 交易所返回的原始数据,
            "exchange": 交易所名称,
            "symbols": ["usdt_btc", "eth_btc", ... ],
            }
        """
        raise NotImplementedError()

    def is_supported_symbol(self, symbol):
        raise NotImplementedError()

    @abstractclassmethod
    def get_exchange_currencies(self):
        """查询当前交易所支持的所有币种

        :return:
            {
            "exchange": 交易所名称,
            "currencies": ["usdt", "btc", ... ],
            }
        """
        raise NotImplementedError()

    @abstractclassmethod
    def get_ticker(self, symbol=None):
        """查询当前市场行情

        :param symbol: 交易对
        :return:
            {
            "raw": 交易所返回的原始数据,
            "high": 最高价,
            "low": 最低价,
            "sell": 卖一价,
            "buy": 买一价,
            "last": 最后成交价,
            "volume": 最近成交量
            }
        """
        raise NotImplementedError()

    @abstractclassmethod
    def get_depth(self, symbol, depth=None):
        """查询当前市场挂单深度
        :param symbol:
        :param depth:  小数位数
        :return:
            {
            "raw": 交易所返回的原始数据,
            "bids": 买盘,[price(成交价), amount(成交量)], 按price降序,,
            "asks": 卖盘,[price(成交价), amount(成交量)], 按price升序,
            }
        """
        raise NotImplementedError()


class QuotationSubscriber:

    @abstractclassmethod
    def subscriber(self, symbol, interval=0):
        raise NotImplementedError()


class PullQuotationSubscriber(QuotationClient, QuotationSubscriber):

    def subscriber(self, symbol, interval=0):
        while True:
            ticker = self.get_ticker(symbol)
            yield ticker
            time.sleep(max(interval, 1))


class ExchangeClient:
    '''
    交易所对象
    '''

    @abstractclassmethod
    def get_assets(self):
        raise NotImplementedError()

    @abstractclassmethod
    def buy(self, symbol, price, amount, type_=None):
        raise NotImplementedError()

    @abstractclassmethod
    def sell(self, symbol, price, amount, type_=None):
        raise NotImplementedError()

    @abstractclassmethod
    def cancel_order(self, order_id):
        raise NotImplementedError()

    @abstractclassmethod
    def get_order(self, order_id):
        raise NotImplementedError()


class Asset:

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=True, indent=2)

    def to_json(self, ensure_ascii=False):
        return json.dumps(self.__dict__, ensure_ascii=ensure_ascii, indent=2)

    def __init__(self, symbol, balance=0):
        self.symbol = symbol
        self.balance = balance
        self.fronzen_balance = 0


class AssetException(Exception):

    def __init__(self, message, asset):
        msg = message + ':' + str(asset)
        Exception.__init__(self, msg)
