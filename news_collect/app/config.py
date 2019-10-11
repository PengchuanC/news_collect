

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
    "商业": ["集团", "华为", "能源内参"],
    "宏观": [
        "楼市", "发改委", "国务院", "财政部", "国资委", "央行", "人民银行", "部委", "部门", "统计局", "CPI", "PPI", "减税",
        "降费", "农业部", "外交部", "交通部", "科创板", "中小板"
    ],
    "金融": [
        "回购", "券商", "银行", "信托", "保险", "理财", "银保监", "证监", "上交所", "深交所", "交易所", "原油", "石油",
        "资管", "证券", "公募", "私募", "房贷", "外汇", "中证", "中基", "协会", "指数", "债", "资本", "基金公司"
           ],
    "日本": ["日本", "野村", "大和", "三井", "三菱"],
}

# 关键字爬虫配置
by_keyword = {
    "eastmoney": ["公募基金", "etf"]
}
