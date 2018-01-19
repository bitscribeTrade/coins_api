# -*- coding:utf-8 -*-

from .apis.binance.API import BinanceAPI
from .contract import PullQuotationSubscriber
from .meta import exchange_api, quotation_provicer

"""
Binance 交易所客户端
{
    "name": "Binance - 币安",
    "API": "https://github.com/binance-exchange/binance-official-api-docs",
    "home_url": "https://www.binance.com/",
}
==============================================================
"""


@exchange_api('Binance', configs=[
    {
        'name': 'biance_api_key',
        'description': 'api_key',
        'type': 'string',
        'required': True
    },
    {
        'name': 'biance_api_secret',
        'description': 'secret_key',
        'type': 'string',
        'required': True
    }
])
@quotation_provicer('Binance')
class BinanceClient(PullQuotationSubscriber):
    """Binance 交易所客户端"""

    def __init__(self, biance_api_key=None, biance_api_secret=None):
        self.name = "Binance"
        self.api_key = biance_api_key
        self.secret_key = biance_api_secret
        self.client = BinanceAPI(self.api_key, self.secret_key)

    @staticmethod
    def _check_transform(symbol):
        return symbol.replace('_', "").replace('/', "").upper()

    """
    基础信息查询 API
    ===========================================================
    """
    # 获取当前所在交易所的相关信息
    @staticmethod
    def get_exchange_info():
        """返回交易所的相关信息，如：名称、网址、API文档地址等"""
        return {
            "name": "Binance - 币安",
            "API": "https://github.com/binance-exchange/binance-official-api-docs",
            "home_url": "https://www.binance.com/",
        }

    # 获取当前所在交易所支持的交易对
    def get_exchange_symbols(self):
        """查询当前交易所支持的所有交易对

        :return:
            {
            "raw": 交易所返回的原始数据,
            "exchange": 交易所名称,
            "symbols": ["usdt_btc", "eth_btc", ... ],
            }
        """
        info = self.client.get_exchange_info()
        info = info['symbols']

        data = {"raw": info, "exchange": self.name}

        symbols = []
        for s in info:
            base = s['baseAsset']
            quote = s['quoteAsset']
            symbol = base + '_' + quote
            symbols.append(symbol.lower())

        data['symbols'] = symbols
        return data

    # 获取当前所在交易所支持的币种
    def get_exchange_currencies(self):
        """查询当前交易所支持的所有币种

        :return:
            {
            "exchange": 交易所名称,
            "currencies": ["usdt", "btc", ... ],
            }
        """
        data = self.get_exchange_symbols()
        currencies = []
        if data['symbols']:
            for i in data['symbols']:
                base, quote = i.split('_')
                currencies.append(base)
                currencies.append(quote)
            return {"exchange": data['exchange'],
                    "currencies": list(set(currencies))}
        else:
            print('get_exchange_symbols方法未定义或调用失败')

    # 获取当前所在交易所的全部API接口
    def get_exchange_apis(self):
        return self.client

    """
    行情查询 API
     ===========================================================
     """

    # - 获取当前市场行情
    def get_ticker(self, symbol):
        """查询当前市场行情，即24h ticker

        :param symbol: 交易对
        :return:
            {
            'symbol': symbol,
            "raw": 交易所返回的原始数据,
            "high": 最高价,
            "low": 最低价,
            "sell": 卖一价,
            "buy": 买一价,
            "last": 最后成交价,
            "volume": 最近成交量,
            "timestamp":时间戳
            }
        """
        raw_symbol = self._check_transform(symbol)
        info = self.client.get_ticker(symbol=raw_symbol)

        ticker = {
            "raw": info,
            'symbol': symbol,
            'raw_symbol': raw_symbol,
            "high": info["highPrice"],
            "low": info["lowPrice"],
            "sell": info["askPrice"],
            "buy": info["bidPrice"],
            "last": info["lastPrice"],
            "volume": info["volume"],
            "timestamp": info['openTime']
        }
        return ticker

    # 获取当前市场挂单深度
    def get_depth(self, symbol):
        """查询当前市场挂单深度

        :param symbol:
        :return:
            {
            "raw": 交易所返回的原始数据,
            "bids": 买盘,[price(成交价), amount(成交量)], 按price降序,,
            "asks": 卖盘,[price(成交价), amount(成交量)], 按price升序,
            }
        """
        symbol = self._check_transform(symbol)
        info = self.client.get_order_book(symbol=symbol)
        bids = info['bids']
        bids = [i[0:2] for i in bids]
        asks = info['asks']
        asks = [i[0:2] for i in asks]
        data = {
            "raw": info,
            "bids": bids,
            "asks": asks,
        }
        return data

    # 获取交易标的最近成交记录（一条）
    def get_trade(self, symbol):
        """查询symbol的最近成交记录

        :param symbol:
        :return:
            {
            "raw": 交易所返回的信息,
            "exchange": 交易所名称,
            "trades": [
                        {"id": 交易所返回的唯一id,
                        "time": 时间Unix timestamp 毫秒,
                        "price": 价格,
                        "amount": 数量,
                        "type": 订单类型:ORDER_TYPE_BUY, ORDER_TYPE_SELL。分别为买单，值为0，卖单，值为1
                        },
                        ...
                        ...
                        ]
            }
        """
        symbol = self._check_transform(symbol)
        info = self.client.get_recent_trades(symbol=symbol, limit=1)
        info = info[0]

        trade = {"id": info['id'],
                 "time": info['time'],
                 "price": info['price'],
                 "amount": info["qty"]}
        if info['isBuyerMaker']:
            trade['type'] = 0
        else:
            trade['type'] = 1

        data = {'raw': info,  "exchange": self.name, "trades": [trade]}
        return data

    # 获取交易标的最近成交记录（多条）
    def get_hist_trades(self, symbol, size=100):
        """查询symbol的最近成交记录（多条）

        :param symbol: 交易对，如：btc_usdt
        :param size: 数量，默认值为 100
        :return:
            {
            "exchange": 交易所名称,
            "raw": 交易所返回的信息,
            "trades": [
                        {"id": 交易所返回的唯一id,
                        "time": 时间Unix timestamp 毫秒,
                        "price": 价格,
                        "amount": 数量,
                        "type": 订单类型:ORDER_TYPE_BUY, ORDER_TYPE_SELL。分别为买单，值为0，卖单，值为1},
                        ...
                        ...
                        ]
            }
        """
        symbol = self._check_transform(symbol)
        infos = self.client.get_recent_trades(symbol=symbol, limit=size)
        trades = []
        for info in infos:
            trade = {"id": info['id'],
                     "time": info['time'],
                     "price": info['price'],
                     "amount": info["qty"]}
            if info['isBuyerMaker']:
                trade['type'] = 0
            else:
                trade['type'] = 1
            trades.append(trade)

        data = {'raw': info, "exchange": self.name, "trades": trades}
        return data

    # 获取最新K线数据
    def get_kline(self, symbol, period='15min', size=100):
        """查询symbol最新的K线数据

        :param symbol: 交易对，如：btc_usdt
        :param period: K线周期，默认值 15min，可选值 1min, 5min, 15min, 30min, 1h, 1day, 1week, 1mon
        :param size: 数量
        :return:
            {
            "exchange": 交易所名称,
            "raw": 交易所返回的信息,
            "klines":[ {
                        "time": 时间Unix timestamp 秒,
                        "open": 价格,
                        "high": 数量,
                        "low": 最低价,
                        "close": 收盘价,
                        "volume": 交易量
                        },
                        ...
                        ...
                    ]
            }
        """

        symbol = self._check_transform(symbol)
        period_to_interval = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "30min": "30m",
            "1h": "1h",
            "1day": "1d",
            "1week": "1w",
            "1mon": "1M",
        }
        period = period_to_interval[period]

        info = self.client.get_klines(
            symbol=symbol, interval=period, limit=size)

        data = {"exchange": self.name, "raw": info}
        klines = []
        for k in info:
            kline = {
                "time": k[0] / 1000,
                "open": k[1],
                "high": k[2],
                "low": k[3],
                "close": k[4],
                "volume": k[5]
            }
            klines.append(kline)

        data['klines'] = klines

        return data

    """
    交易转账 API
    ===========================================================
    """

    # 下买单
    def buy(self, symbol, amount, type_=1, price=None):
        """买入symbol

        :param symbol:
        :param price: 价格
        :param amount: 下单数量
        :param type_: 市价单（0） or 限价单（1），默认值为限价单
        :return:
            order_id: 订单id
        """
        symbol = self._check_transform(symbol=symbol)
        if type_ == 1:
            info = self.client.order_limit_buy(symbol=symbol, quantity=amount,
                                               price=str(price))
        else:
            info = self.client.order_market_buy(symbol=symbol, quantity=amount)
        return info["orderId"]

    # 下卖单
    def sell(self, symbol, amount, type_=1, price=None):
        """卖出symbol

        :param symbol:
        :param price: 价格
        :param amount: 下单数量
        :param type_: 市价单（0） or 限价单（1），默认值为限价单
        :return:
            order_id: 订单id
        """
        symbol = self._check_transform(symbol=symbol)

        if type_ == 1:
            info = self.client.order_limit_sell(symbol=symbol, quantity=amount,
                                                price=str(price))
        else:
            info = self.client.order_market_sell(
                symbol=symbol, quantity=amount)

        return info["orderId"]

    # 取消一个订单
    def cancel_order(self, order_id, symbol):
        """取消一个订单

        :param order_id: 需要取消的订单id
        :return:
            {"order_id": 订单id,
            "submitted": 是否成功提交撤单申请，成功为 True}
        """
        symbol = self._check_transform(symbol=symbol)
        info = self.client.cancel_order(symbol=symbol, orderId=order_id)
        if info:
            return {"order_id": order_id, "submitted": True}
        else:
            return {"order_id": order_id, "submitted": False}

    # 查询某个订单详情
    def get_order(self, order_id, symbol):
        """查询某个订单详情

        :param order_id: 需要查询的订单id
        :return:
            {
            "raw": 交易所返回的原始信息,
            "id": 订单唯一标识符,
            "price": 下单价格,
            "amount": 下单数量,
            "deal_amount": 成交数量,
            "status": 订单状态, PENDING : 未完成 CLOSED :已完成 CANCELED : 已取消,
            "type": 订单类型, BUY :买单，SELL : 卖单
            }
        """
        symbol = self._check_transform(symbol=symbol)
        info = self.client.get_order(symbol=symbol, orderId=order_id)
        data = {'raw': info,
                "id": info['orderId'],
                "price": info['price'],
                "amount": info["origQty"],
                "deal_amount": info["executedQty"]}

        # add status
        if info['status'] == self.client.ORDER_STATUS_CANCELED:
            data['status'] = "CANCELED"
        elif info['status'] == self.client.ORDER_STATUS_FILLED:
            data['status'] = "CLOSED"
        else:
            data['status'] = "PENDING"

        # add type
        if info['side'] == "BUY":
            data['type'] = "BUY"
        else:
            data['type'] = "SELL"

        return data

    # 提现、转账
    @staticmethod
    def withdraw():
        """提现、转账

        :param address: 提现地址，务必确认是对应币种的地址 str
        :param currency: 数字货币，如：btc
        :param amount: 提现数量 float
        :return:
            {"success": 布尔值，转账成功返回True}

        """
        print("币安取消了withdraw API")

    # 查询账户余额
    def get_assets(self):
        """查询账户余额

        :return:
            非空数字资产余额
            {
            "raw": 交易所返回的元素信息,
            "exchange": 交易所名称,
            "balances": [
                        {'balance': '0.000000000000000000', 'currency': 'ast', 'type': 'frozen'},
                        {'balance': '0.000000000000000000', 'currency': 'bat', 'type': 'trade'}
                        ],
            }
        """
        info = self.client.get_account()
        data = {"raw": info, "exchange": self.name}

        info = info['balances']
        balances = []
        for b in info:
            currency = b['asset'].lower()
            if float(b['free']) != 0.000:
                balance = {'balance': b['free'],
                           'currency': currency, 'type': 'trade'}
                balances.append(balance)
            elif float(b['locked']) != 0.000:
                balance = {'balance': b['locked'],
                           'currency': currency, 'type': 'frozen'}
                balances.append(balance)

        data['balances'] = balances
        return data
