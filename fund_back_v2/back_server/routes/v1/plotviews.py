from pandas import cut
from math import ceil

from flask_restful import Api, Resource, marshal_with, fields, reqparse

from . import rest
from ...models import Classify, IndicatorsForPlot as IFP, BasicInfo, db


api = Api(rest, prefix="/plot")


@api.resource("/branch")
class BranchView(Resource):
    def get(self):
        latest = Classify.query.with_entities(Classify.update_date).order_by(Classify.update_date.desc()).first()[0]
        classify = Classify.query.with_entities(Classify.branch, Classify.classify).filter_by(
            update_date=latest).distinct().all()
        branch = list(set([x[0] for x in classify]))
        bc = {x: [] for x in branch}
        for c in classify:
            bc[c[0]].append(c[1])
        ret = {"data": bc, "branch": branch}
        return ret


@api.resource("/exist")
class ExistViews(Resource):
    def get(self):
        classify = parse_classify()
        ret = ExistViews.process(classify)
        return ret

    @staticmethod
    def process(classify):
        latest = IFP.query.with_entities(IFP.update_date).order_by(IFP.update_date.desc()).first()[0]
        funds = query_funds_by_classify(classify)
        data = IFP.query.with_entities(IFP.fund_setupdate).filter(
            IFP.update_date == latest, IFP.windcode.in_(funds)).all()
        data = [x[0] for x in data]
        years = [(latest - x).days / 365 for x in data]
        mean = sum(years) / len(years)
        _max = max(years)
        years = cut(years, bins=range(0, ceil(_max)), labels=range(0, ceil(_max) - 1))
        years = (years.value_counts() / len(years)).to_dict()
        years = [{"存续年限": x, "频率分布": y} for x, y in years.items() if y != 0]
        years = sorted(years, key=lambda x: x['存续年限'])
        ret = {"data": years, "mean": mean, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


@api.resource("/scale")
class ScaleViews(Resource):
    def get(self):
        classify = parse_classify()
        ret = ScaleViews.process(classify)
        return ret

    @staticmethod
    def process(classify):
        latest = IFP.query.with_entities(IFP.update_date).order_by(IFP.update_date.desc()).first()[0]
        funds = query_funds_by_classify(classify)
        data = IFP.query.with_entities(IFP.prt_netasset).filter(
            IFP.update_date == latest, IFP.windcode.in_(funds)).all()
        data = [x[0] / (10 ** 8) for x in data if x[0]]
        _max = max(data)
        count = len(data)
        # 将x轴20等分
        data = cut(data, bins=range(0, ceil(_max / 20) * 20 - ceil(_max / 20), ceil(_max / 20)))
        data = (data.value_counts() / count).to_dict()
        data = [{"规模分布": (int(x.left), int(x.right)), "频率分布": y} for x, y in data.items() if y]
        ret = {"data": data, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


@api.resource("/comp")
class CompanyViews(Resource):
    def get(self):
        classify = parse_classify()
        ret = CompanyViews.process(classify)
        return ret

    @staticmethod
    def process(classify):
        latest = IFP.query.with_entities(IFP.update_date).order_by(IFP.update_date.desc()).first()[0]
        funds = query_funds_by_classify(classify)
        data = IFP.query.with_entities(IFP.prt_netasset, IFP.fund_corp_fundmanagementcompany).filter(
            IFP.update_date == latest, IFP.windcode.in_(funds)).all()
        data = [x for x in data if x[0]]
        company = list(set([x[1] for x in data]))
        company = {x: 0 for x in company}
        for x in data:
            company[x[1]] += x[0] / (10 ** 8)
        company = [{"基金公司": x, "基金资产": y} for x, y in company.items()]
        company = sorted(company, key=lambda x: x['基金资产'], reverse=True)
        cumsum = sum(x['基金资产'] for x in company)
        cum = 0
        for i in range(0, len(company)):
            cum += company[i]['基金资产']
            company[i]['占比'] = cum / cumsum
        ret = {"data": company, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


@api.resource("/scale&year")
class ScaleYearViews(Resource):
    def get(self):
        classify = parse_classify()
        ret = ScaleYearViews.process(classify)
        return ret

    @staticmethod
    def process(classify):
        latest = IFP.query.with_entities(IFP.update_date).order_by(IFP.update_date.desc()).first()[0]
        funds = query_funds_by_classify(classify)
        data = db.session.query(BasicInfo.sec_name, IFP.prt_netasset, IFP.fund_setupdate).join(
            IFP, BasicInfo.windcode == IFP.windcode).join(
            Classify, BasicInfo.windcode == Classify.windcode).filter(
            IFP.windcode.in_(funds), Classify.classify == classify, IFP.update_date == latest).all()
        data = [
            {"基金简称": x[0], "基金规模": round(x[1] / (10 ** 8), 2),
             "存续时间": round((latest - x[2]).days / 365, 2)}
            for x in data if x[0] if all({x[1], x[2]})
        ]
        data = sorted(data, key=lambda x: x["存续时间"])
        data = [{"基金简称": x["基金简称"], "存续时间": x["存续时间"], "基金规模": x["基金规模"], "近似年限": int(x["存续时间"])} for x in data]
        ret = {"data": data, "classify": classify, "date": latest.strftime("%Y-%m-%d")}
        return ret


@api.resource("/")
class PlotViews(Resource):
    def get(self):
        classify = parse_classify()
        exist_data = ExistViews.process(classify)
        scale_data = ScaleViews.process(classify)
        comp = CompanyViews.process(classify)
        sc_y = ScaleYearViews.process(classify)
        return {"data": {
            "exist": exist_data["data"], "scale": scale_data["data"], 'company': comp["data"], "scale_year": sc_y["data"]
        }, "classify": classify, "date": exist_data['date']}


def parse_classify():
    parser = reqparse.RequestParser()
    parser.add_argument("classify", type=str)
    args = parser.parse_args()
    classify = args.get("classify")
    return classify


def query_funds_by_classify(classify):
    latest = Classify.query.with_entities(Classify.update_date).order_by(Classify.update_date.desc()).first()[0]
    funds = Classify.query.with_entities(Classify.windcode).filter(
        Classify.classify == classify, Classify.update_date == latest).all()
    funds = list({x[0] for x in funds})
    return funds
