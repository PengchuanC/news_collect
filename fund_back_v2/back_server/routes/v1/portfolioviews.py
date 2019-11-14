import pandas as pd

from flask_restful import Api, Resource, marshal_with, fields, reqparse

from . import rest

from ...models import Portfolio, PortfolioObserve, PortfolioCore, db, Indicators, BasicInfo, FundPerformance


api = Api(rest)


resource_fields = {
        "id": fields.Integer,
        "port_id": fields.Integer,
        "windcode": fields.String,
        "update_date": fields.String
    }


@api.resource("/portfolio")
class PortfolioViews(Resource):
    resource_field = {
        "port_id": fields.Integer,
        "port_name": fields.String,
        "port_type": fields.Integer,
    }

    @marshal_with(resource_field)
    def get(self):
        ret = Portfolio.query.all()
        return ret


@api.resource("/portfolio/info")
class PortfolioInfoViews(Resource):
    resource_fields = {
        "基金代码": fields.String,
        "基金简称": fields.String,
        "成立日期": fields.String,
        "基金规模(亿元)": fields.String,
        "基金资产": fields.String,
        "当前净值": fields.String,
        "累计净值": fields.String,
        "近1周回报": fields.String,
        "近1月回报": fields.String,
        "近3月回报": fields.String,
        "近6月回报": fields.String,
        "近1年回报": fields.String,
        "近3年回报": fields.String,
        "成立年化回报": fields.String,
    }

    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("port_id", type=str)
        parser.add_argument("type", type=str)
        args = parser.parse_args()
        port_id = args.get("port_id")
        _type = args.get("type")

        latest = PortfolioCore.query.with_entities(db.func.max(PortfolioCore.update_date)).first()[0]

        if _type == "核心池":
            ret = PortfolioCore.query.with_entities(PortfolioCore.windcode).filter(
                PortfolioCore.port_id == port_id,
                PortfolioCore.update_date == latest
            ).all()
        else:
            ret = PortfolioObserve.query.with_entities(PortfolioObserve.windcode).filter(
                PortfolioObserve.port_id == port_id,
                PortfolioObserve.update_date == latest
            ).all()

        ret = [x[0] for x in ret]

        basic_info = BasicInfo.query.with_entities(
            BasicInfo.windcode, BasicInfo.sec_name, BasicInfo.setup_date
        ).filter(
            BasicInfo.windcode.in_(ret)
        ).all()

        basic_info = pd.DataFrame(basic_info).set_index("windcode")

        latest_ind = Indicators.query.with_entities(db.func.max(Indicators.update_date)).first()[0]
        indicators = Indicators.query.with_entities(
            Indicators.windcode, Indicators.numeric, Indicators.indicator
        ).filter(
            Indicators.indicator.in_(["NETASSET_TOTAL", "FUND_FUNDSCALE"]),
            Indicators.update_date == latest_ind,
            Indicators.windcode.in_(ret)
        ).all()

        indicators = pd.DataFrame(indicators)
        indicators["numeric"] = indicators["numeric"].astype("float")
        indicators = indicators.pivot("windcode", "indicator")["numeric"]
        indicators = indicators / 1e8

        latest_performance = FundPerformance.query.with_entities(db.func.max(FundPerformance.update_date)).first()[0]

        performance = FundPerformance.query.with_entities(
            FundPerformance.windcode, FundPerformance.indicator, FundPerformance.value
        ).filter(
            FundPerformance.windcode.in_(ret),
            FundPerformance.update_date == latest_performance
        ).all()

        performance = pd.DataFrame(performance).pivot("windcode", "indicator")["value"]

        df = pd.merge(basic_info, indicators, left_index=True, right_index=True, how="inner")
        df = pd.merge(df, performance, left_index=True, right_index=True, how="inner")
        df = df.rename(columns={
            "sec_name": "基金简称", "setup_date": "成立日期", 'FUND_FUNDSCALE': "基金规模(亿元)",
            'NETASSET_TOTAL': "基金资产",  'NAV': "当前净值", 'NAV_ACC': "累计净值",
            'RETURN_1M': "近1月回报", 'RETURN_1Y': "近1年回报",
            'RETURN_3M': "近3月回报", 'RETURN_3Y': "近3年回报",
            'RETURN_6M': "近6月回报", 'RETURN_STD': "成立年化回报",
            'RETURN_1W': "近1周回报"
        })
        df['成立日期'] = df['成立日期'].apply(lambda x: x.strftime("%Y/%m/%d"))
        df["基金代码"] = df.index
        for col in ["基金规模(亿元)", "基金资产", "当前净值", "累计净值", "近1月回报", "近3月回报", "近6月回报", "近1年回报", "近3年回报", "成立年化回报", "近1周回报"]:
            df[col] = df[col].apply(lambda x: round(x, 2))
        ret = df.to_dict(orient="record")
        return ret
