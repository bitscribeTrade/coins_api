class QuotationProviderMeta:
    """
    行情提供者
    """

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=True, indent=2)

    def to_json(self, ensure_ascii=False):
        return json.dumps(self.__dict__, ensure_ascii=ensure_ascii, indent=2)

    def __init__(self):
        self.name = '未命名'
        self.desctription = ''
        self.configs = []
        '''
            config 定义
            {
                name:string,
                required:boolean
                type:string|number
            }
        '''

    def add_config(self, name: str, type_: str, required=False):
        for c in self.configs:
            # 如果名称相同且required优先级更高
            if c['name'] == name and required:
                c['name'].required
                return
        self.configs.append({
            'name': name,
            'type': type_,
            'required': required
        })


class ExchangeApiMeta:
    """
    行情提供者
    """

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=True, indent=2)

    def to_json(self, ensure_ascii=False):
        return json.dumps(self.__dict__, ensure_ascii=ensure_ascii, indent=2)

    def __init__(self):
        self.name = '未命名'
        self.desctription = ''
        self.configs = []
        '''
            config 定义
            {
                name:string,
                required:boolean
                type:string|number
            }
        '''

    def add_config(self, name: str, type_: str, required=False):
        for c in self.configs:
            # 如果名称相同且required优先级更高
            if c['name'] == name and required:
                c['name'].required
                return
        self.configs.append({
            'name': name,
            'type': type_,
            'required': required
        })


def quotation_provicer(name, description='', configs=[]):
    """
    标记一个行情提供者
        :param name:
        :param description='':
        :param configs=None:
    """
    def meta(cls):
        meta = QuotationProviderMeta()
        meta.configs = configs
        meta.name = name
        meta.description = description
        cls.__quotation_provicer_meta__ = meta
        return cls
    return meta


def exchange_api(name, description='', configs=[]):
    """
    标记一个交易所Api
        :param name:
        :param description='':
        :param configs=None:
    """
    def meta(cls):
        meta = ExchangeApiMeta()
        meta.configs = configs
        meta.name = name
        meta.description = description
        cls.__exchange_api_meta__ = meta
        return cls
    return meta
