# -*- coding:utf-8 -*-
"""
Huobi 交易所客户端
{
    "name": "Huobi - 火币网",
    "API": "https://github.com/huobiapi/API_Docs/wiki",
    "home_url": "https://www.huobi.pro/zh-cn/",
}
==============================================================
"""

from .base_client import Client
from .apis.huobi.API import HuobiAPI
from .contract import PullQuotationSubscriber
from .meta import exchange_api, quotation_provicer


@exchange_api('Huobi', configs=[
    {
        'name': 'huobi_api_key',
        'description': 'api_key',
        'type': 'string',
        'required': True
    },
    {
        'name': 'huobi_api_secret',
        'description': 'secret_key',
        'type': 'string',
        'required': True
    }
])
@quotation_provicer('Huobi')
class HuobiClient(PullQuotationSubscriber):
    """统一API客户端"""

    def __init__(self, huobi_api_key=None, huobi_api_secret=None):
        self.name = "Huobi"
        self.client = HuobiAPI(huobi_api_key, huobi_api_secret)
        if huobi_api_key is not None and huobi_api_secret is not None:
            self.accounts = self.client.get_accounts()
            self.spot_acc_id = self.accounts[0]['id']  # 现货账户id
        self.order_ids = {"buy": [], "sell": [], "cancel": []}

    @staticmethod
    def _check_transform(symbol):
        return symbol.lower().replace('_', "").replace('/', "")

    """
    基础信息查询 API
    =====================================================================================
    """

    # 获取当前所在交易所的相关信息
    @staticmethod
    def get_exchange_info():
        return {
            "name": "Huobi - 火币网",
            "API": "https://github.com/huobiapi/API_Docs/wiki",
            "home_url": "https://www.huobi.pro/zh-cn/",
        }

    # 获取当前所在交易所支持的交易对
    def get_exchange_symbols(self):
        raw = self.client.get_symbols()
        data = {"raw": raw, "exchange": self.name}
        symbols = []
        for d in raw['data']:
            symbol = d['base-currency'] + '_' + d['quote-currency']
            symbols.append(symbol)
        data['symbols'] = symbols
        return data

    """
    行情查询 API
    =====================================================================================
    """

    # 获取当前市场行情
    def get_ticker(self, symbol):
        """查询当前市场行情

        :param symbol: 交易对， 如：btc_usdt
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

        raw_symbol = self._check_transform(symbol)
        # symbol = symbol.lower().replace('_', "")
        res = self.client.get_merged(symbol=raw_symbol)
        if res['status'] == "ok":
            data = res['tick']
        ticker = {"raw": data,
                  'symbol': symbol,
                  'raw_symbol': raw_symbol,
                  'high': data['high'],
                  'low': data['low'],
                  'sell': data['ask'][0],
                  'buy': data['bid'][0],
                  'last': data['close'],
                  'volume': data['vol'],
                  'timestamp': res['ts']
                  }

        return ticker

    # 获取当前市场挂单深度
    def get_depth(self, symbol, type="step0"):
        """查询当前市场挂单深度

        :param symbol: 交易对， 如：btc_usdt
        :param type: Depth类型 	step0, step1, step2, step3, step4, step5（合并深度0-5）；step0时，不合并深度
        :return:
            {
            "raw": 交易所返回的原始数据,
            "bids": 买盘,[price(成交价), amount(成交量)], 按price降序,,
            "asks": 卖盘,[price(成交价), amount(成交量)], 按price升序,
            }
        """
        symbol = self._check_transform(symbol)

        info = self.client.get_depth(symbol, type=type)
        bids = info['tick']['bids']
        asks = info['tick']['asks']
        data = {"raw": info, "bids": bids, "asks": asks}
        return data

    # 获取交易标的最近成交记录（一条）
    def get_trade(self, symbol):
        """查询symbol的最近成交记录(仅返回一条)

        :param symbol: 交易对，如：btc_usdt
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
        # symbol = symbol.lower().replace('_', "")
        data = {"exchange": self.name}
        trades = []
        info = self.client.get_trade(symbol)
        data['raw'] = info
        tick = info['tick']
        trade = {"id": tick['id'],
                 "time": tick['ts'],
                 "price": tick['data'][0]['price'],
                 "amount": tick['data'][0]['amount']}
        if tick['data'][0]['direction'] == "buy":
            trade['type'] = 0
        else:
            trade['type'] = 1
        trades.append(trade)
        data['trades'] = trades
        return data

    # 获取交易标的最近成交记录（多条）
    def get_hist_trades(self, symbol, size=100):
        """查询symbol的最近成交记录（多条）

        :param symbol: 交易对，如：btc_usdt
        :param size: 数量，默认值为 1 取值范围 1 - 2000
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
        data = {"exchange": self.name}
        trades = []
        info = self.client.get_hist_trade(symbol, size=size)
        data['raw'] = info
        for tick in info['data']:
            trade = {"id": tick['id'],
                     "time": tick['ts'],
                     "price": tick['data'][0]['price'],
                     "amount": tick['data'][0]['amount']}
            if tick['data'][0]['direction'] == "buy":
                trade['type'] = 0
            else:
                trade['type'] = 1
            trades.append(trade)
        data['trades'] = trades
        return data

    # 获取最新K线数据
    def get_kline(self, symbol, period='15min', size=100):
        """查询symbol最新的K线数据

        :param symbol: 交易对，如：btc_usdt
        :param period: K线周期，默认值 15min，可选值 1min, 5min, 15min, 30min, 1h, 1day, 1week, 1mon
        :param size: 数量, 默认值 100， 取值范围 1-2000
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
        symbol = self._check_transform(symbol)

        period_to_interval = {
            "1min": "1min",
            "5min": "5min",
            "15min": "15min",
            "30min": "30min",
            "1h": "60min",
            "1day": "1day",
            "1week": "1week",
            "1mon": "1mon",
        }
        period = period_to_interval[period]
        info = self.client.get_kline(symbol, period=period, size=size)
        data = {
            "exchange": self.name,
            "raw": info
        }

        klines = []

        for k in info['data']:
            kline = {
                "time": k['id'],
                "open": k['open'],
                "high": k['high'],
                "low": k['low'],
                "close": k['close'],
                "volume": k['vol']
            }
            klines.append(kline)

        data['klines'] = klines

        return data

    """
    交易转账 API
    =====================================================================================
    """

    # 下买单
    def buy(self, symbol, price, amount, type_=1):
        """买入symbol

        :param symbol:
        :param price: 价格
        :param amount: 下单数量
        :param type_: 市价单（0） or 限价单（1），默认值为限价单
        :return:
            order_id: 订单id
        """
        acc_id = self.spot_acc_id
        symbol = self._check_transform(symbol)

        if type_ == 1:
            info = self.client.orders(acct_id=acc_id, price=price,
                                      symbol=symbol, amount=amount,
                                      type="buy-limit")
        else:
            info = self.client.orders(acct_id=acc_id, price=price,
                                      symbol=symbol, amount=amount,
                                      type="buy-market")
        if info['status'] == 'ok':
            self.order_ids['buy'].append(info['data'])
            return info['data']
        else:
            print("下买单失败！")

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
        acc_id = self.spot_acc_id
        symbol = self._check_transform(symbol)
        if type_ == 1:
            info = self.client.orders(acct_id=acc_id, price=price,
                                      symbol=symbol, amount=amount,
                                      type="sell-limit")
        else:
            info = self.client.orders(acct_id=acc_id, price=price,
                                      symbol=symbol, amount=amount,
                                      type="sell-market")
        if info['status'] == 'ok':
            self.order_ids['sell'].append(info['data'])
            return info['data']
        else:
            print("下买单失败！")

    # 查询账户现有订单

    # 取消一个订单
    def cancel_order(self, order_id):
        """取消一个订单

        :param order_id: 需要取消的订单id
        :return:
            {"order_id": 订单id,
            "submitted": 是否取消成功，成功为 True}
        """
        if order_id not in self.order_ids['buy'] \
                and order_id not in self.order_ids['sell']:
            raise ValueError('输入的 order_id 不在列表中，请检查！')
        data = {"order_id": order_id}
        info = self.client.cancel_order(order_id=order_id)
        if info['status'] == 'ok':
            self.order_ids['cancel'].append(info['data'])
            data['submitted'] = True
        else:
            data['submitted'] = False
        return data

    # 批量取消多个订单
    def cancel_orders(self, order_ids):
        """批量取消多个订单

        :param order_ids:  list/str 需要取消的订单列表，
        如果order_ids='all', 则取消订单列表中的所有订单 火币限制不能超过50个订单
        :return:
            {
            "success_submitted": 成功提交撤单的订单列表,
            "fail_submitted": 撤单提交失败的订单列表
            }
        """
        info = self.client.batch_cancel_order(order_ids=order_ids)
        if info['status'] == "ok":
            success_submitted = info['data']['success']
            self.order_ids['cancel'] = success_submitted
            fail_submitted = info['data']['failed']

            data = {
                "success_submitted": success_submitted,
                "fail_submitted": fail_submitted
            }

            return data
        else:
            print(info)

    # 查询某个订单详情
    def get_order(self, order_id):
        """查询某个订单详情

        :param order_id: 需要查询的订单id
        :return:
            {
            "raw": 交易所返回的原始信息,
            "id": 订单唯一标识符,
            "price": 下单价格,
            "amount": 下单数量,
            "deal_amount": 成交数量,
            "status": 订单状态, pending : 未完成 closed :已完成 canceled : 已取消,
            "type": 订单类型, buy :买单，sell : 卖单
            }
        """
        info = self.client.order_info(order_id=order_id)
        if info['status'] == 'ok':
            data = {'raw': info,
                    "id": info['data']['id'],
                    "price": info['data']['price'],
                    "amount": info['data']['amount'],
                    "deal_amount": info['data']['field-amount']
                    }

            # status
            if info['data']['state'] == 'filled':
                data['status'] = "closed"
            elif info['data']['state'] == 'canceled':
                data['status'] = "canceled"
            else:
                data['status'] = "pending"

            # type
            if "buy" in info['data']['type']:
                data['type'] = "buy"
            else:
                data['type'] = "sell"

        return data

    # 提现、转账
    def withdraw(self, address, currency, amount, addr_tag=""):
        """提现、转账

        :param address: 提现地址，务必确认是对应币种的地址 str
        :param currency: 数字货币，如：btc
        :param amount: 提现数量 float
        :param addr_tag: 虚拟币共享地址tag，XRP特有 格式, "123"类的整数字符串
        :return:
            {"row": 交易所返回的原始信息,
            "success": 布尔值，转账成功返回True}
        """
        data = {"row": None, "success": False}
        info = self.client.withdraw(
            address, amount, currency, addr_tag=addr_tag)
        data['row'] = info
        if info['status'] == 'ok':
            data['success'] = True
        return data

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
        balances = []
        info = []
        for acc in self.accounts:
            acct_id = acc['id']
            bs = self.client.get_balance(acct_id)
            info.append(bs)
            for b in bs['data']['list']:  # 解析，仅保留余额大于0的资产
                if float(b['balance']) > 0.00:
                    balances.append(b)
        data['info'] = info
        data['balances'] = balances
        return data
