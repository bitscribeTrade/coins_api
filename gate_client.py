# -*- coding:utf-8 -*-

from .apis.gate.API import GateAPI
import time

"""
Gate 交易所客户端
{
    "name": "Gate.io",
    "API": "https://gate.io/api2",
    "home_url": "https://gate.io/",
}
==============================================================
"""


class GateClient:
    """统一API客户端"""

    def __init__(self, api_key=None, secret_key=None):
        self.name = "Gate"
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = GateAPI(self.api_key, self.secret_key)

    @staticmethod
    def _check_transform(symbol):
        if "_" not in symbol:
            print("symbol 规则：基础币种+计价币种。如BTC/USDT，"
                  "symbol为btc_usdt；ETH/BTC， symbol为eth_btc，以此类推。")
        else:
            return symbol

    """
    基础信息查询 API
    ===========================================================
    """
    # 获取当前所在交易所的相关信息
    @staticmethod
    def get_exchange_info():
        """返回交易所的相关信息，如：名称、网址、API文档地址等"""
        return {"name": "Gate",
                "API": "https://gate.io/api2",
                "home_url": "https://gate.io/"}

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
        data = {"raw": None, "exchange": self.name, "symbols": None}
        symbols = self.client.pairs()
        data['raw'] = symbols
        data["symbols"] = symbols
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
            raise NotImplementedError('get_exchange_symbols方法未定义或调用失败')

    # 获取当前所在交易所的全部API接口
    def get_exchange_apis(self):
        return self.client

    """
    行情查询 API
    ===========================================================
    """

    # 获取当前市场行情
    def get_ticker(self, symbol):
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
            "volume": 最近成交量,
            "timestamp":时间戳
            }
        """
        symbol = self._check_transform(symbol=symbol)
        info = self.client.ticker(symbol)

        data = {
            "raw": info,
            "high": info["high24hr"],
            "low": info["low24hr"],
            "sell": info["lowestAsk"],
            "buy": info["highestBid"],
            "last": info['last'],
            "volume": info['quoteVolume'],
            "timestamp": int(time.time() * 1000)
        }

        return data

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
        symbol = self._check_transform(symbol=symbol)
        info = self.client.orderBook(symbol)
        if info['result'] == "true":
            return {"raw": info, "bids": info['bids'], "asks": info['asks']}
        else:
            raise Exception("depth数据获取失败")

    # 获取交易标的最近成交记录（一条）
    def get_trade(self, symbol):
        """查询symbol的最近成交记录

        :param symbol:
        :return:
            {
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
        symbol = self._check_transform(symbol=symbol)
        info = self.client.tradeHistory(symbol)
        assert info['result'] == "true", '历史交易记录获取失败'
        data = {"exchange": self.name, "raw": info}

        trades = []
        t = info["data"][-1]
        trade = {
            "id": t["tradeID"],
            "time": t["timestamp"] + '000',
            "price": t['rate'],
            "amount": t['amount']
        }

        if t['type'] == "sell":
            trade['type'] = 1
        else:
            trade['type'] = 0

        trades.append(trade)
        data['trades'] = trades

        return data

    # 获取交易标的最近成交记录（多条）
    def get_hist_trades(self, symbol=None, size=100):
        """查询symbol的最近成交记录（多条）

        :param symbol: 交易对，如：btc_usdt
        :param size: 数量，默认值为 1
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
        symbol = self._check_transform(symbol=symbol)
        info = self.client.tradeHistory(symbol)
        assert info['result'] == "true", '历史交易记录获取失败'
        data = {"exchange": self.name, "raw": info}

        trades = []
        for t in info["data"]:
            trade = {
                "id": t["tradeID"],
                "time": t["timestamp"] + '000',
                "price": t['rate'],
                "amount": t['amount']
            }

            if t['type'] == "sell":
                trade['type'] = 1
            else:
                trade['type'] = 0

            trades.append(trade)
        if size < len(trades):
            trades = trades[-size:-1]
        data['trades'] = trades

        return data

    # 获取最新K线数据
    def get_kline(self, symbol=None, period='15min', size=100):
        """查询symbol最新的K线数据

        :param symbol: 交易对，如：btc_usdt
        :param period: K线周期，默认值 15min，可选值 1min, 5min, 15min, 30min, 1h, 1day, 1week, 1mon
        :param size: 数量
        :return:
            {
            "exchange": 交易所名称,
            "raw": 交易所返回的信息,
            "klines":[ {
                        "time": 时间Unix timestamp 毫秒,
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
        raise Exception('Gate没有提供 kline 相关API')

    """
    交易转账 API
    ===========================================================
    """

    # 下买单
    def buy(self, symbol, price, amount, type_=1):
        """买入symbol

        :param symbol:
        :param price: 价格
        :param amount: 下单数量
        :param type_: 市价单（0） or 限价单（1），默认值为限价单
        :return:
            {
            'symbol': 交易对
            'order_id': 订单id
            }
        """
        symbol = self._check_transform(symbol=symbol)
        assert type_ == 1, "Gate 没有提供市价单下单接口"
        info = self.client.buy(currencyPair=symbol, rate=price,
                               amount=amount)
        assert info['result'] == 'true', "下单失败，请检查！"
        return {
            'symbol': symbol,
            'order_id': info['orderNumber']
        }

    # 下卖单
    def sell(self, symbol, price, amount, type_=1):
        """卖出symbol

        :param symbol:
        :param price: 价格
        :param amount: 下单数量
        :param type_: 市价单（0） or 限价单（1），默认值为限价单
        :return:
            order_id: 订单id
        """
        symbol = self._check_transform(symbol=symbol)
        assert type_ == 1, "Gate 没有提供市价单下单接口"
        info = self.client.sell(currencyPair=symbol, rate=price,
                                amount=amount)
        assert info['result'] == 'true', "下单失败，请检查！"
        return {
            'symbol': symbol,
            'order_id': info['orderNumber']
        }

    # 取消一个订单
    def cancel_order(self, symbol, order_id):
        """取消一个订单
        :param symbol: 交易对
        :param order_id: 需要取消的订单id
        :return:
            {"order_id": 订单id,
            "submitted": 是否取消成功，成功为 True}
        """
        info = self.client.cancelOrder(orderNumber=order_id,
                                       currencyPair=symbol)
        if info['result'] == "true":
            return {"order_id": order_id, "submitted": True}
        else:
            return {"order_id": order_id, "submitted": False}

    # 批量取消多个订单
    def cancel_orders(self, order_ids):
        """批量取消多个订单

        :param order_ids: list/str 需要取消的订单列表，
        如果order_ids='all', 则取消订单列表中的所有订单
        :return:
            {
            "success_submitted": 成功提交撤单的订单列表,
            "fail_submitted": 撤单提交失败的订单列表
            }
        """
        raise NotImplementedError("取消多个订单的接口还没有实现")

    # 查询某个订单详情
    def get_order(self, symbol, order_id):
        """查询某个订单详情

        :param order_id: 需要查询的订单id
        :return:
            {
            "raw": 交易所返回的原始信息,
            "id": 订单唯一标识符,
            "price": 下单价格,
            "amount": 下单数量,
            "deal_amount": 成交数量,
            "status": 订单状态,
                    PENDING : 未完成
                    CLOSED :已完成
                    CANCELED : 已取消,
            "type": 订单类型, BUY :买单，SELL : 卖单
            }
        """
        info = self.client.getOrder(orderNumber=order_id, currencyPair=symbol)

        assert info['result'] == "true", "获取订单详情失败"
        data = {
            "raw": info,
            "id": info['order']['id'],
            "price": info['order']['initialRate'],
            "amount": info['order']['initialAmount'],
            "deal_amount": info['order']['amount']
        }

        # add status
        if info['order']['status'] == 'cancelled':
            data['status'] = "CANCELED"
        else:
            data['status'] = "CLOSED"

        # add type
        if info['order']['type'] == 'sell':
            data['type'] = "SELL"
        else:
            data['type'] = "BUY"

        return data

    # - 批量查询多个订单详情
    def get_orders(self, order_ids):
        """批量查询多个订单详情

        :param order_ids: 需要查询的订单id列表
        :return:
            {
            "raw": 交易所返回的原始信息,
            "orders": [
                {
                "id": 订单唯一标识符,
                "price": 下单价格,
                "amount": 下单数量,
                "deal_amount": 成交数量,
                "status": 订单状态, PENDING : 未完成 CLOSED :已完成 CANCELED : 已取消,
                "type": 订单类型, BUY :买单，SELL : 卖单
                },
                ...
                ...
            ]
            }
        """
        raise NotImplementedError("批量查询多个订单详情接口还没有实现")

    # 提现、转账
    def withdraw(self, address, currency, amount):
        """提现、转账

        :param address: 提现地址，务必确认是对应币种的地址 str
        :param currency: 数字货币，如：btc
        :param amount: 提现数量 float
        :return:
            {"success": 布尔值，转账成功返回True}

        """
        info = self.client.withdraw(currency=currency, amount=amount,
                                    address=address)
        if info['result'] == 'true':
            return {"success": True}
        else:
            return {"success": False}

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
        data = {"exchange": self.name}
        info = self.client.balances()
        if isinstance(info, str):
            info = eval(info)
        data['raw'] = info

        balances = []
        for b in info["available"].items():
            currency = b[0].lower()
            balance = {'balance': b[1], 'currency': currency, 'type': 'trade'}
            balances.append(balance)

        data['balances'] = balances
        return data
