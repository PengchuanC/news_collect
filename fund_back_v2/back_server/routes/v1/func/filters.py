from datetime import timedelta
from functools import lru_cache
from math import floor, pow

from sqlalchemy import and_, or_
import pandas as pd

from back_server import cache
from ....models import Indicators, db, BasicInfo, Classify


@lru_cache(20)
def latest_day_in_basic_info():
    latest = db.session.query(db.func.max(BasicInfo.update_date)).first()[0]
    return latest


@lru_cache(20)
def latest_day_in_indicators():
    latest = db.session.query(db.func.max(Indicators.update_date)).first()[0]
    return latest


@lru_cache(20)
def latest_day_in_classify():
    latest = db.session.query(db.func.max(Classify.update_date)).first()[0]
    return latest


@cache.cached()
def funds_by_classify(cls: list):
    """获取特定分类下的全部基金"""
    c = Classify
    latest = latest_day_in_classify()
    funds = db.session.query(c.windcode).filter(c.classify.in_(cls), c.update_date == latest).all()
    funds = {x[0] for x in funds}
    return funds


@cache.cached()
def lever(funds, yes_or_no):
    """是否是杠杆基金"""
    BI = BasicInfo
    funds = db.session.query(BI.windcode, BI.structured).filter(BI.windcode.in_(funds)).all()
    funds = {x[0] for x in funds if x[1] == yes_or_no}
    return funds


@cache.cached()
def fund_years(funds, left, right=50):
    """基金存续时间位于[left, right]"""
    c = BasicInfo
    latest = latest_day_in_basic_info()
    left = latest - timedelta(left * 365)
    right = latest - timedelta(right * 365)
    funds = db.session.query(c.windcode).filter(c.setup_date.between(right, left), c.windcode.in_(funds)).all()
    funds = set([x[0] for x in funds])
    return funds


@cache.cached()
def net_asset(funds, recent_asset_level, avg_asset_level):
    """对最新一期季报和年报的基金净值规模作出要求"""
    ins = Indicators
    rpt = db.session.query(db.func.distinct(ins.rpt_date)).order_by(db.desc(ins.rpt_date)).all()
    rpt = [x[0] for x in rpt]
    recent = rpt[0]
    annual = [x for x in rpt if x.month == 12][0]
    funds = db.session.query(ins.windcode).filter(
        ins.windcode.in_(funds), ins.rpt_date == recent, ins.indicator == "NETASSET_TOTAL",
                                 ins.numeric >= recent_asset_level * 1e8
    ).all()
    funds = {x[0] for x in funds}
    funds = db.session.query(ins.windcode).filter(
        ins.windcode.in_(funds), ins.rpt_date == annual, ins.indicator == "PRT_AVGNETASSET",
                                 ins.numeric >= avg_asset_level * 1e8
    ).all()
    funds = {x[0] for x in funds}
    return funds


@cache.cached()
def single_hold_shares(funds, percent: int = 40):
    """单一投资者持仓比例限制，默认低于40%"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "HOLDER_SINGLE_TOTALHOLDINGPCT", ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] < percent}
    return funds


@cache.cached()
def over_index_return(funds, index_code, year):
    """区间收益超过指定的指数的区间收益"""
    index_code = index_code.split(",")
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RETURN", ins.windcode.in_(funds)
    ).all()
    index = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RETURN", ins.windcode.in_(index_code),
        ins.note == str(year)
    ).all()
    if len(index_code) == 1:
        index = index[0]
        funds = {x[0] for x in funds if x[1] > index[1]}
    elif len(index_code) == 2:
        index = (index[0][1]+index[1][1]) / 2
        funds = {x[0] for x in funds if x[1] > index}
    return funds


@cache.cached()
def over_bench_return(funds, year):
    """区间收益超过基准
    此处应当注意如易方达中小盘等采用天相指数的基金，wind并没有相关数据，此处跳过这些检查，让基准收益 >= 0
    """
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "NAV_OVER_BENCH_RETURN_PER", ins.note == str(year),
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= 0}
    return funds


@cache.cached()
def month_win_ratio(funds, year, ratio=0.5):
    """月度胜率"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.text, "0/0")).filter(
        ins.update_date == latest, ins.indicator == "ABSOLUTE_UPDOWNMONTHRATIO", ins.note == str(year),
        ins.windcode.in_(funds)
    ).all()

    _funds = []
    for fund in funds:
        up, down = fund[1].split("/")
        if int(down) == 0:
            _funds.append(fund[0])
        else:
            if int(up)/int(down) > ratio:
                _funds.append(fund[0])

    return _funds


@cache.cached()
def max_downside_over_average(funds, year, ratio=None):
    """最大回撤优于平均"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RISK_MAXDOWNSIDE", ins.note == str(year),
        ins.windcode.in_(funds)
    ).all()
    if str(ratio) == "平均":
        mmd = [x[1] for x in funds]
        mean = sum(mmd) / len(mmd)
        funds = {x[0] for x in funds if x[1] > mean}
    else:
        funds = {x[0] for x in funds if x[1]/100 > -ratio}
    return funds


@cache.cached()
def corp_scale_level(funds, level):
    """基金公司规模大于？分位"""
    ins = Indicators
    latest_c = latest_day_in_classify()
    latest_i = latest_day_in_indicators()
    all_funds = db.session.execute(
        f'SELECT a.windcode, a.text, IFNULL(b.numeric, 0) FROM t_ff_indicator_for_filter a JOIN t_ff_indicator_for_filter b ON a.windcode = b.windcode JOIN t_ff_classify c ON a.windcode = c.windcode where a.update_date = "{latest_i}" and c.UPDATE_DATE = "{latest_c}" and a.indicator = "FUND_CORP_FUNDMANAGEMENTCOMPANY" AND b.indicator = "FUND_FUNDSCALE"; '
    ).fetchall()
    corps = {x[1] for x in all_funds}
    corps = {x: 0 for x in corps}
    for x in all_funds:
        corps[x[1]] += x[2]
    corps = list(zip(corps.items()))
    corps = [x[0] for x in corps]
    corps = sorted(corps, key=lambda x: x[1], reverse=True)
    corps = corps[: floor(len(corps) * level)]
    corps = {x[0] for x in corps}
    funds = db.session.query(ins.windcode, ins.text).filter(
        ins.indicator == "FUND_CORP_FUNDMANAGEMENTCOMPANY", ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] in corps}
    return funds


@cache.cached()
def manager_working_years(funds, year):
    """基金经历工作年满？年"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "FUND_MANAGER_MANAGERWORKINGYEARS",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= year}
    return funds


@cache.cached()
def manager_working_years_on_this_fund(funds, year):
    """基金经历在本基金任职年限超过？年"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0) / 365).filter(
        ins.update_date == latest, ins.indicator == "FUND_MANAGER_ONTHEPOSTDAYS",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= year}
    return funds


@cache.cached()
def manager_geometry_return(funds, annual_return):
    """基金经历年化回报"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "FUND_MANAGER_GEOMETRICANNUALIZEDYIELD",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= annual_return}
    return funds


@cache.cached()
def manager_return_on_this_fund(funds, annual_return):
    """任职本基金年化回报"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "NAV_PERIODICANNUALIZEDRETURN",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= annual_return}
    return funds


@cache.cached()
def wind_rating(funds, rating=3):
    """Wind评级超过？星，默认大于等于3星"""
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RATING_WIND3Y",
        ins.windcode.in_(funds)
    ).all()
    funds = {x[0] for x in funds if x[1] >= rating}
    return funds


@cache.cached()
def recent_years_over_others(funds, year, level):
    """最近X年收益均超过？%分位"""
    f = funds
    ins = Indicators
    latest = latest_day_in_indicators()
    funds = db.session.query(ins.windcode, db.func.ifnull(ins.numeric, 0)).filter(
        ins.update_date == latest, ins.indicator == "RETURN", ins.note == str(year)
    ).all()
    funds = [(x[0], x[1]) for x in funds]
    funds = sorted(funds, key=lambda x: x[1], reverse=True)
    funds = funds[: floor(len(funds) * level)]
    funds = {x[0] for x in funds}
    funds = {x for x in f if x in funds}
    return funds


def execute_basic_filter(data):
    """执行简单的筛选规则，传入参数为前端POST请求参数"""
    # print(data)
    if data["classify"]:
        classify = [x.split("-")[-1] for x in data["classify"]]
        funds = funds_by_classify(classify)
    else:
        return -1
    if data["lever"]:
        funds = lever(funds, data["lever"])
    if data["existYear"]:
        funds = fund_years(funds, data["existYear"])
    if data["netValue"]:
        funds = net_asset(funds, data["netValue"], data["netValue"])
    if data["singleHolder"]:
        funds = single_hold_shares(funds, data["singleHolder"])
    if data["overIndex"]:
        funds = over_index_return(funds, data["overIndex"], data["existYear"])
    if data["overBench"] == "是":
        funds = over_bench_return(funds, data["existYear"])
    if data["monthWin"]:
        funds = month_win_ratio(funds, data["existYear"], data["monthWin"])
    if data["maxDownside"]:
        funds = max_downside_over_average(funds, data["existYear"], data["maxDownside"])
    return funds


def execute_advance_filter(funds, f):
    """执行高级筛选功能，需要筛选规则f"""
    if f["overCorps"]:
        funds = corp_scale_level(funds, f["overCorps"])
    if f["workYear"]:
        funds = manager_working_years(funds, f["workYear"])
    if f["workOnThis"]:
        funds = manager_return_on_this_fund(funds, f["workOnThis"])
    if f["geoReturn"]:
        funds = manager_geometry_return(funds, f["geoReturn"] * 100)
    if f["thisReturn"]:
        funds = manager_return_on_this_fund(funds, f["thisReturn"] * 100)
    if f["windRating"]:
        funds = wind_rating(funds, f["windRating"])
    if f["recentLevel"]:
        levels = f["recentLevel"]
        for level in levels:
            level = level[1: -1]
            year, level = level.split(", ")
            level = level.split("/")
            funds = recent_years_over_others(funds, int(year), float(level[0]) / float(level[1]))
    return funds


def basic_info(funds, page):
    """获取基金基础信息"""
    update_date = db.session.query(db.func.max(Classify.update_date)).one()[0]
    ret = db.session.query(
        Classify.classify, Classify.branch, BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.fund_benchmark,
        BasicInfo.setup_date
    ).join(BasicInfo, and_(Classify.windcode == BasicInfo.windcode)).filter(
        Classify.update_date == update_date, BasicInfo.windcode.in_(funds)).paginate(page, 25)
    return ret


def fund_details(funds, filters, page=None):
    """
    基金详细信息
    :param page: 后端分页面
    :param funds: 基金列表
    :param filters: 筛选规则
    :return: 基金详细信息
    """
    date = latest_day_in_indicators()
    year = filters['existYear'] if filters['existYear'] else 1
    rpt = db.session.query(db.func.distinct(Indicators.rpt_date)).filter(Indicators.update_date == date).order_by(Indicators.rpt_date.desc()).first()[0]

    names = BasicInfo.query.with_entities(db.func.distinct(BasicInfo.windcode), BasicInfo.sec_name, BasicInfo.setup_date).filter(BasicInfo.windcode.in_(funds))
    if page:
        p = names.paginate(page, 50)
        names = p.items
        page = p.page
        per_page = p.per_page
        total = p.total
    else:
        names = names.all()
        page = None
        per_page = None
        total = None
    names = {x[0]: (x[1], x[2]) for x in names}

    data = Indicators.query \
        .filter(Indicators.update_date == date, Indicators.windcode.in_(names.keys())) \
        .filter(or_(Indicators.note == year, Indicators.note.is_(None))) \
        .filter(Indicators.rpt_date == rpt).all()
    data = [x.to_dict() for x in data]
    codes = list({x['windcode'] for x in data})

    ret = {x: {} for x in codes}
    for x in data:
        if x["windcode"] in (names.keys()):
            ret[x["windcode"]][x["indicator"]] = round(float(x["numeric"]), 2) if x["numeric"] else x['text']
            ret[x["windcode"]]["sec_name"] = names[x["windcode"]][0]
            ret[x["windcode"]]["setup"] = names[x["windcode"]][1].strftime("%Y/%m/%d")

    ret = [
        {
            "windCode": x, "corp": y["FUND_CORP_FUNDMANAGEMENTCOMPANY"],
            "winRatio": y["ABSOLUTE_UPDOWNMONTHRATIO"],
            "scale": y["FUND_FUNDSCALE"]/1e8 if y["FUND_FUNDSCALE"] else y["FUND_FUNDSCALE"],
            "managerAnnualReturn": y["FUND_MANAGER_GEOMETRICANNUALIZEDYIELD"],
            "workingYears": y["FUND_MANAGER_MANAGERWORKINGYEARS"],
            "workingOnThis": round(y["FUND_MANAGER_ONTHEPOSTDAYS"]/365, 2),
            "singleHold": y["HOLDER_SINGLE_TOTALHOLDINGPCT"],
            "overBench": y["NAV_OVER_BENCH_RETURN_PER"],
            "workingAnnualReturn": y["NAV_PERIODICANNUALIZEDRETURN"],
            "netAsset": y["PRT_FUNDNETASSET_TOTAL"],
            "rating": int(y["RATING_WIND3Y"]) if y["RATING_WIND3Y"] else y["RATING_WIND3Y"],
            "return": (pow(1+y["RETURN"]/100, 1/year)-1)*100 if y["RETURN"] else None,
            "maxDownSide": y["RISK_MAXDOWNSIDE"],
            "secName": y["sec_name"],
            "existYear": year,
            "setup": y["setup"],
            "update": date.strftime("%Y/%m/%d")
        }
        for x, y in ret.items()]

    return ret, page, per_page, total


def fund_details_to_excel(funds, filters):
    data, *_ = fund_details(funds, filters)
    data = pd.DataFrame(data)
    data.to_excel("./back_server/static/筛选结果.xlsx")
