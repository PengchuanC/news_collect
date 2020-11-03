import os


# 数据库
database = {
    "user": "fund",
    "password": "123456",
    "host": "localhost",
    "port": 3306,
    "db": "fund_filter"
}


# 远程数据库
database_remote = {
    "user": "fund",
    "password": "123456",
    "host": "cdb-p3ccshwm.cd.tencentcdb.com",
    "port": 10053,
    "db": "fund_filter"
}


# 爬虫参数
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/77.0.3865.90 Safari/537.36",
    "Referer": "",
}


# 任务执行周期
task_cycle = {"hour": 1, "min": 0, "second": 0}


# 网站分布
website = {
    "eastmoney": {
        "金融": [{"section": "金融", "path": "news/czqyw", "page": 1}],
        "日本": [{"section": "日本", "path": "news/cgjjj", "page": 1}],
        "商业": [{"section": "商业", "path": "a/csyzx", "page": 1}]
    },
    "caixin": {
        "宏观": [{"section": "宏观", "path": "economy", "page": 1}],
        "金融": [{"section": "金融", "path": "finance", "page": 1}],
        "商业": [{"section": "商业", "path": "companies", "page": 1}]
    },
    "chinasecurity": {
        "宏观": [{"section": "宏观", "path": "", "page": 0}]
    },
    "sina": {
        "金融": [{"section": "金融", "path": "", "page": 1}]
    },
    "kyodo": {
        "日本": [
            {"section": "日本", "path": "economy_science", "page": 1},
            {"section": "日本", "path": "japan-china_relationship", "page": 1},
            {"section": "日本", "path": "japan_politics", "page": 1}
        ]
    }
}


# 各板块下可能包含的关键字
keyword = {
    "商业": [
        "集团", "能源内参", "重组",
        "华为", "中兴", "百度", "阿里", "腾讯", "京东", "拼多多", "万科", "恒大",
    ],
    "宏观": [
        "国务院", "国资委", "部委", "发改委", "财政部", "商务部", "外交部", "住建部", "交通部", "工信部", "水利部", "农业部",
        "文化部", "国土", "海关", "税务", "环保", "中宣部", "教育部", "外交部", "国防部", "科技部",
        "gdp", "GDP", "产值", "生产总值", "PMI", "pmi", "失业率", "就业率", "增加值", "企业利润", "固投", "固定资产投资", "房地产",
        "社消", "社会消费", "汽车", "出口", "财政", "汇率", "社融", "M2", "m2", "CPI", "cpi", "PPI", "ppi", "猪肉", "原油", "减税",
        "降费", "楼市",
    ],
    "金融": [
        "回购", "券商", "银行", "信托", "保险", "理财", "银保监", "证监", "上交所", "深交所", "交易所", "原油", "石油", "资管",
        "证券", "公募", "私募", "房贷", "外汇", "中证", "中基", "协会", "指数", "债", "资本", "基金公司", "科创板", "MSCI",
        "中小板",
        "央行", "人民银行", "人行", "证监", "银保监", "监管机构", "交易所", "上交所", "深交所", "港交所", "中基协", "基金业", "中证协",
        "证券业", "银行业协会", "保险业协会",
        "证券公司", "券商", "资管", "基金", "理财", "信托", "保险", "私募", "msci", "MSCI", "沪港通", "深港通",
        "早盘", "内参"
    ],
    "日本": [
        "日本", "日本央行", "日央行", "东京交易所",
        "日经", "topix", "TOPIX", "野村", "日经", "大和", "三井", "三菱", "瑞穗", "日兴", "顶峰", "软银"
    ],
}

# 各板块下不应包含的关键字，或该关键字代表的新闻不重要
ignore = [
    "IPO", "ipo", "发行", "过会", "审批", "收盘"
]


# 关键字爬虫配置
by_keyword = {
    "eastmoney": ["公募基金", "etf"],
    "hibor": ["配置"]
}

# 项目路径
base_dir = os.path.dirname(__file__)
