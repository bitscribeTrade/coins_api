# -*- coding: utf-8 -*-

"""
https://github.com/huobiapi/API_Docs/wiki/REST_api_reference
@author zengbin
创建日期：2018-01-06
======================================================================================
"""


from .hb_util import MARKET_URL
from .hb_util import http_get_request
from .hb_util import api_key_get
from .hb_util import api_key_post


class HuobiAPI:
    """
    火币API客户端
    """

    def __init__(self, ACCESS_KEY=None, SECRET_KEY=None):
        self.name = "Huobi"
        self.API_HOST = "api.huobi.pro"
        self.ACCESS_KEY = ACCESS_KEY
        self.SECRET_KEY = SECRET_KEY
        # if self.ACCESS_KEY is not None and self.SECRET_KEY is not None:
        #     self.ACCOUNT_ID = self.get_accounts()  # 获取key对应的accounts，分为 spot（现货账户） 和 otc
        #     self.spot_acct_id = self.ACCOUNT_ID[0]['id']
        # else:
        #     print("Huobi Client：没有设置keys，只能使用详情查询类API")

    """
    Rest API 详情
    ==================================================================================
    """
    # 获取KLine
    @staticmethod
    def get_kline(symbol, period, size):
        """\获取KLine
        kline 接口详细介绍：
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-markethistorykline-%E8%8E%B7%E5%8F%96k%E7%BA%BF%E6%95%B0%E6%8D%AE

        symbol      交易对，如：btcusdt
        period      可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        size        获取数量：默认150，取值范围 1 - 2000
        long_polling    可选值： { true, false }

        example
              get_kline('btcusdt', "15min", size=10)
        """
        params = {'symbol': symbol,
                  'period': period,
                  'size': size}
        url = MARKET_URL + '/market/history/kline'  # K线数据接口
        info = http_get_request(url, params)
        assert info['status'] == "ok", "%s" % str(info)
        return info

    # 获取聚合行情(Ticker)
    @staticmethod
    def get_merged(symbol):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-marketdetailmerged-%E8%8E%B7%E5%8F%96%E8%81%9A%E5%90%88%E8%A1%8C%E6%83%85ticker
        :param symbol: 火币支持的所有交易对
        :return:

        example
            get_merged('btcusdt')
        """
        params = {'symbol': symbol}
        url = MARKET_URL + '/market/detail/merged'
        return http_get_request(url, params)

    # 获取 Market Depth 数据
    @staticmethod
    def get_depth(symbol, type):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-marketdepth-%E8%8E%B7%E5%8F%96-market-depth-%E6%95%B0%E6%8D%AE
        symbol  可选值：{ btcusdt }
        type    可选值：{ step0, step1, step2, step3, step4, step5 }

        example
            get_depth('btcusdt', type="step1")
        """
        params = {'symbol': symbol,
                  'type': type}
        url = MARKET_URL + '/market/depth'
        return http_get_request(url, params)

    # 获取 Trade Detail 数据
    @staticmethod
    def get_trade(symbol):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-markettrade-%E8%8E%B7%E5%8F%96-trade-detail-%E6%95%B0%E6%8D%AE

        :param symbol: 可选值：{ ethcny }
        :return:

        example
            get_trade('btcusdt')
        """
        params = {'symbol': symbol}
        url = MARKET_URL + '/market/trade'
        return http_get_request(url, params)

    # 批量获取最近的交易记录
    @staticmethod
    def get_hist_trade(symbol, size):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-markethistorytrade-%E6%89%B9%E9%87%8F%E8%8E%B7%E5%8F%96%E6%9C%80%E8%BF%91%E7%9A%84%E4%BA%A4%E6%98%93%E8%AE%B0%E5%BD%95

        :param symbol: 可选值：{ btcusdt }
        :param size: 获取交易记录的数量  默认值 1， 取值范围 1 - 2000
        :return:

        example
            get_hist_trade('btcusdt')
        """
        params = {'symbol': symbol, 'size': size}
        url = MARKET_URL + '/market/history/trade'
        return http_get_request(url, params)

    # 获取 Market Detail 24小时成交量数据
    @staticmethod
    def get_detail(symbol):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-marketdetail-%E8%8E%B7%E5%8F%96-market-detail-24%E5%B0%8F%E6%97%B6%E6%88%90%E4%BA%A4%E9%87%8F%E6%95%B0%E6%8D%AE
        :param symbol: 可选值：{ btcusdt }
        :return:
        """
        params = {'symbol': symbol}
        url = MARKET_URL + '/market/detail'
        return http_get_request(url, params)

    """
    Rest API 公共
    ==================================================================================
    """
    # 查询系统支持的所有交易对及精度
    @staticmethod
    def get_symbols():
        """\
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1commonsymbols-%E6%9F%A5%E8%AF%A2%E7%B3%BB%E7%BB%9F%E6%94%AF%E6%8C%81%E7%9A%84%E6%89%80%E6%9C%89%E4%BA%A4%E6%98%93%E5%AF%B9%E5%8F%8A%E7%B2%BE%E5%BA%A6
        查询系统支持的所有交易对
        """
        url = MARKET_URL + '/v1/common/symbols'
        params = {}
        return http_get_request(url, params)

    # 查询系统支持的所有币种
    @staticmethod
    def get_currencys():
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1commoncurrencys-%E6%9F%A5%E8%AF%A2%E7%B3%BB%E7%BB%9F%E6%94%AF%E6%8C%81%E7%9A%84%E6%89%80%E6%9C%89%E5%B8%81%E7%A7%8D
        """
        url = MARKET_URL + '/v1/common/currencys'
        params = {}
        return http_get_request(url, params)

    # 查询系统当前时间
    @staticmethod
    def get_timestamp():
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1commontimestamp-%E6%9F%A5%E8%AF%A2%E7%B3%BB%E7%BB%9F%E5%BD%93%E5%89%8D%E6%97%B6%E9%97%B4
        """
        url = MARKET_URL + '/v1/common/timestamp'
        params = {}
        return http_get_request(url, params)

    """
    Rest API 用户资产
    ==================================================================================
    """

    def _check_keys(self):
        if self.ACCESS_KEY is not None and self.SECRET_KEY is not None:
            return True
        else:
            print("Huobi Client：没有设置keys，只能使用详情查询类API")
            return False

    # 查询当前用户的所有账户(即account-id)
    def get_accounts(self):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1accountaccounts-%E6%9F%A5%E8%AF%A2%E5%BD%93%E5%89%8D%E7%94%A8%E6%88%B7%E7%9A%84%E6%89%80%E6%9C%89%E8%B4%A6%E6%88%B7%E5%8D%B3account-id
        """
        path = "/v1/account/accounts"
        params = {}
        accounts = api_key_get(params, path, self.ACCESS_KEY, self.SECRET_KEY)
        return accounts['data']

    # 查询指定账户的余额
    def get_balance(self, acct_id):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1accountaccountsaccount-idbalance-%E6%9F%A5%E8%AF%A2%E6%8C%87%E5%AE%9A%E8%B4%A6%E6%88%B7%E7%9A%84%E4%BD%99%E9%A2%9D
        :param acct_id
        :return:
        """
        url = "/v1/account/accounts/{0}/balance".format(acct_id)
        params = {"account-id": acct_id}
        return api_key_get(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    """
    Rest API 交易
    ==================================================================================
    """
    # 下单

    def orders(self, acct_id, amount, symbol, price, type, source=None):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#post-v1orderordersplace-%E4%B8%8B%E5%8D%95
        :param amount:
        :param acct_id: 账户id
        :param source:
        :param symbol:
        :param type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price:
        :return:
        """
        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": symbol,
                  "type": type,
                  "source": source,
                  "price": price}
        url = "/v1/order/orders/place"
        return api_key_post(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 申请撤销一个订单请求
    def cancel_order(self, order_id):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#post-v1orderordersorder-idsubmitcancel--%E7%94%B3%E8%AF%B7%E6%92%A4%E9%94%80%E4%B8%80%E4%B8%AA%E8%AE%A2%E5%8D%95%E8%AF%B7%E6%B1%82
        :param order_id:
        :return:
        """
        params = {}
        url = "/v1/order/orders/{0}/submitcancel".format(order_id)
        return api_key_post(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 批量撤销订单
    def batch_cancel_order(self, order_ids):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#post-v1orderordersbatchcancel-%E6%89%B9%E9%87%8F%E6%92%A4%E9%94%80%E8%AE%A2%E5%8D%95
        :param order_ids: list 	撤销订单ID列表 	单次不超过50个订单id
        :return:
        """
        params = {"order-ids": order_ids}
        url = "/v1/order/orders/batchcancel"
        return api_key_post(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 查询某个订单详情
    def order_info(self, order_id):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1orderordersorder-id-%E6%9F%A5%E8%AF%A2%E6%9F%90%E4%B8%AA%E8%AE%A2%E5%8D%95%E8%AF%A6%E6%83%85
        :param order_id:
        :return:
        """
        params = {}
        url = "/v1/order/orders/{0}".format(order_id)
        return api_key_get(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 查询某个订单的成交明细
    def order_matchresults(self, order_id):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1orderordersorder-idmatchresults--%E6%9F%A5%E8%AF%A2%E6%9F%90%E4%B8%AA%E8%AE%A2%E5%8D%95%E7%9A%84%E6%88%90%E4%BA%A4%E6%98%8E%E7%BB%86
        :param order_id:
        :return:
        """
        params = {}
        url = "/v1/order/orders/{0}/matchresults".format(order_id)
        return api_key_get(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 查询当前委托、历史委托
    def orders_list(self, symbol, states, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1orderorders-%E6%9F%A5%E8%AF%A2%E5%BD%93%E5%89%8D%E5%A7%94%E6%89%98%E5%8E%86%E5%8F%B2%E5%A7%94%E6%89%98
        :param symbol:
        :param states: 可选值 {pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销}
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: 可选值{prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol,
                  'states': states}

        if types:
            params['types'] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/v1/order/orders'
        return api_key_get(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 查询当前成交、历史成交
    def orders_matchresults(self, symbol, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#get-v1ordermatchresults-%E6%9F%A5%E8%AF%A2%E5%BD%93%E5%89%8D%E6%88%90%E4%BA%A4%E5%8E%86%E5%8F%B2%E6%88%90%E4%BA%A4
        :param symbol:
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: 可选值{prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol}

        if types:
            params['types'] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/v1/order/matchresults'
        return api_key_get(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    """
    Rest API 虚拟币提现  仅支持提现到【Pro站提币地址列表中的提币地址】
    ==================================================================================
    """

    # 申请提现虚拟币
    def withdraw(self, address, amount, currency, fee=0, addr_tag=""):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#post-v1dwwithdrawapicreate-%E7%94%B3%E8%AF%B7%E6%8F%90%E7%8E%B0%E8%99%9A%E6%8B%9F%E5%B8%81
        :param address: 提现地址
        :param amount: 提币数量
        :param currency:btc, ltc, bcc, eth, etc ...(火币Pro支持的币种)
        :param fee: 转账手续费
        :param addr-tag: 虚拟币共享地址tag，XRP特有
        :return: {
                  "status": "ok",
                  "data": 700
                }
        """
        params = {'address': address,
                  'amount': amount,
                  "currency": currency,
                  "fee": fee,
                  "addr-tag": addr_tag}
        url = '/v1/dw/withdraw/api/create'
        return api_key_post(params, url, self.ACCESS_KEY, self.SECRET_KEY)

    # 申请取消提现虚拟币
    def cancel_withdraw(self, address):
        """
        https://github.com/huobiapi/API_Docs/wiki/REST_api_reference#post-v1dwwithdraw-virtualwithdraw-idcancel-%E7%94%B3%E8%AF%B7%E5%8F%96%E6%B6%88%E6%8F%90%E7%8E%B0%E8%99%9A%E6%8B%9F%E5%B8%81
        :param address:
        :return: {
                  "status": "ok",
                  "data": 700
                }
        """
        params = {}
        url = '/v1/dw/withdraw-virtual/{0}/cancel'.format(address)
        return api_key_post(params, url, self.ACCESS_KEY, self.SECRET_KEY)
