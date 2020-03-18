from flask_restful import Api, Resource, fields, marshal_with, reqparse, request

import pandas as pd
import numpy as np

from . import rest

from ...models import FundPerformance, db, Style, Classify, FundNav, IndexClosePrice, Index
from ...models import BasicInfo
from .func.util import DateUtil, date

fs = Api(rest, prefix="/fundinfo")

resource_fields = {
    "data": fields.List(fields.Nested({
        "id": fields.Integer,
        "windcode": fields.String,
        "indicator": fields.String,
        "value": fields.Float,
        "update_date": fields.String
    })),
    "sec_name": fields.String
}


def windcode_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("windcode", type=str)
    args = parser.parse_args()
    windcode = args.get("windcode")
    return windcode


def latest_update_date(model):
    latest = model.query.with_entities(db.func.max(model.update_date)).first()[0]
    return latest


@fs.resource("/")
class Performance(Resource):

    def get(self):
        windcode = windcode_parser()
        fp = FundPerformance
        sec_name = BasicInfo.query.with_entities(BasicInfo.sec_name).filter_by(windcode=windcode).first()[0]
        max_update_date = fp.query.with_entities(fp.update_date).filter(
            fp.windcode == windcode
        ).order_by(fp.update_date.desc()).first()[0]
        ret = fp.query.filter(fp.windcode == windcode).filter(fp.update_date == max_update_date).all()
        data = {"update_date": max_update_date.strftime("%Y-%m-%d"), "sec_name": sec_name}
        for r in ret:
            data[r.indicator] = r.value
        return data


@fs.resource("/style")
class StyleViews(Resource):
    resource_fields = {
        "windcode": fields.String,
        "small_value": fields.Float,
        "small_growth": fields.Float,
        "mid_value": fields.Float,
        "mid_growth": fields.Float,
        "large_value": fields.Float,
        "large_growth": fields.Float,
        "bond": fields.Float,
        "value_date": fields.String,
        "freq": fields.String
    }

    @marshal_with(resource_fields)
    def get(self):
        windcode = windcode_parser()

        ret = Style.query.filter(Style.windcode == windcode).all()
        return ret


@fs.resource("/style&benchmark")
class StyleAndBenchmarkViews(Resource):
    def get(self):
        benchmark = Index.query.with_entities(Index.windcode, Index.sec_name).filter(
            Index.kind == "normal"
        ).all()
        style = Index.query.with_entities(Index.windcode, Index.sec_name).filter(
            Index.kind == "invest_style"
        ).all()
        return {"benchmark": benchmark, "style": style}


@fs.resource("/plotperformance")
class PlotPerformanceViews(Resource):
    def post(self):
        return PlotPerformanceViews.compute()

    @staticmethod
    def compute():
        """整理基金业绩表现数据，附带股票指数和行业指数"""
        params = request.json
        windcode = params.get("windcode")
        is_in = FundNav.query.with_entities(FundNav.windcode).filter(FundNav.windcode == windcode).first()
        if not is_in:
            return {"msg": -1, "info": f"{windcode} is not in FundNav"}
        name = BasicInfo.query.with_entities(BasicInfo.sec_name).filter(BasicInfo.windcode == windcode).first()[0]
        style = params.get("style")
        benchmark = params.get("benchmark", "000300.SH")
        if not benchmark:
            benchmark = "000300.SH"
        benchmark_name = Index.query.with_entities(Index.sec_name).filter(Index.windcode == benchmark).first()[0]
        if not style:
            basic_style = {"股票类": "885012.WI", "债券类": "885005.WI", "货币类": "885009.WI",
                           "另类": "885010.WI", "QDII": "885054.WI", "FOF": "885010.WI"}
            latest = latest_update_date(Classify)
            branch = Classify.query.with_entities(Classify.branch).filter(Classify.update_date == latest).first()[0]
            style = basic_style.get(branch, "885010.WI")
        style_name = Index.query.with_entities(Index.sec_name).filter(Index.windcode == style).first()[0]
        start = FundNav.query.with_entities(db.func.min(FundNav.date)).first()[0]
        nav_adj = FundNav.query.with_entities(FundNav.nav_adj, FundNav.date).filter(
            FundNav.windcode == windcode, FundNav.date >= start
        ).all()
        style_cp = IndexClosePrice.query.with_entities(IndexClosePrice.close, IndexClosePrice.date).filter(
            IndexClosePrice.windcode == style, IndexClosePrice.date >= start
        ).all()
        bench_cp = IndexClosePrice.query.with_entities(IndexClosePrice.close, IndexClosePrice.date).filter(
            IndexClosePrice.windcode == benchmark, IndexClosePrice.date >= start
        ).all()
        nav_adj = pd.DataFrame(nav_adj).set_index("date")
        style_cp = pd.DataFrame(style_cp).set_index("date")
        bench_cp = pd.DataFrame(bench_cp).set_index("date")
        data = pd.merge(nav_adj, style_cp, how="left", left_index=True, right_index=True)
        data = pd.merge(data, bench_cp, how="left", left_index=True, right_index=True)
        data.columns = ["fund", "style", "benchmark"]

        performance = PlotPerformanceViews.performance(data)
        performance["name"] = [name, style_name, benchmark_name]
        performance = performance.to_dict(orient="records")

        year_performance = PlotPerformanceViews.yearly_performance(data)
        yp_t = year_performance.T
        year_performance["name"] = [name, style_name, benchmark_name]
        yp_t.columns = [name, style_name, benchmark_name]
        yp_t["year"] = yp_t.index
        year_performance_chart = yp_t.to_dict(orient="records")
        year_performance = year_performance.to_dict(orient="records")

        data = data.fillna(method="bfill")
        data = data / data.iloc[0, :] - 1
        data = data.apply(lambda x: round(x, 4))
        data["date"] = data.index
        data["date"] = data["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        data = data.to_dict(orient="list")

        return {"data": data, "fund": name, "style": style_name, "benchmark": benchmark_name,
                "performance": performance, "yearly": year_performance, "yearly_chart": year_performance_chart,
                "msg": 0}

    @staticmethod
    def performance(data: pd.DataFrame):
        """|index|fund|style|benchmark|"""
        dates = list(data.index)
        table = pd.DataFrame()
        date = dates[-1]
        du = DateUtil(date)
        ytd = du.ytd()
        end = -1
        start = 0
        if ytd not in dates:
            ytd = not_in_series()
        else:
            ytd = dates.index(ytd)
        table["ytd"] = round((data.iloc[end] / data.iloc[ytd] - 1) * 100, 2)

        m3 = du.x_months_ago(3)
        if m3 not in dates:
            m3 = not_in_series()
        else:
            m3 = dates.index(m3)
        table["m3"] = round((data.iloc[end] / data.iloc[m3] - 1) * 100, 2)

        m6 = du.x_months_ago(6)
        if m6 not in dates:
            m6 = not_in_series()
        else:
            m6 = dates.index(m6)
        table["m6"] = round((data.iloc[end] / data.iloc[m6] - 1) * 100, 2)

        for x in [1, 2, 3, 5]:
            y = du.x_years_ago(x)
            if y not in dates:
                y = not_in_series()
            else:
                y = dates.index(y)
            table[f"y{x}"] = round((data.iloc[end] / data.iloc[y] - 1) * 100, 2)

        total = round((data.iloc[end] / data.iloc[start] - 1) * 100, 2)
        table["total"] = total

        annual = round((np.power(1+total, 365/len(dates)) - 1)*100, 2)
        table["annual"] = annual

        return table

    @staticmethod
    def yearly_performance(data):
        """|index|fund|style|benchmark|"""
        data = data[data.index >= date(date.today().year-5, 1, 1)]
        dates = list(data.index)
        start = dates[0]
        end = dates[-1]
        start_y = start.year
        end_y = end.year
        table = pd.DataFrame()
        for y in range(start_y, end_y):
            if y == start_y:
                d1 = dates.index(start)
            else:
                d1 = dates.index(date(y-1, 12, 31))
            d2 = dates.index(date(y, 12, 13))
            table[f"{y}"] = round((data.iloc[d2]/data.iloc[d1]-1)*100, 2)
        ytd = dates.index(date(end_y-1, 12, 31))
        table["ytd"] = round((data.iloc[-1]/data.iloc[ytd]-1)*100, 2)
        return table


def not_in_series():
    return pd.Series([None, None, None], index=["fund", "style", "benchmark"])
