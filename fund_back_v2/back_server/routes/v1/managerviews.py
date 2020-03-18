from flask_restful import Api, Resource, marshal_with, fields, reqparse

from . import rest

from ...models import FundManager, Classify, BasicInfo, Indicators, Funds


api = Api(rest, prefix="/manager")


resource_fileds = {
    "id": fields.Integer,
    "windcode": fields.String,
    "manager": fields.String(attribute="fund_fundmanager"),
    "predmanager": fields.String(attribute="fund_predfundmanager"),
    "company": fields.String(attribute="fund_corp_fundmanagementcompany"),
    "update_date": fields.String,
    "manager_info": fields.List(fields.Nested({
        "netasset": fields.Float(attribute="fund_manager_totalnetasset"),
        "resume": fields.String(attribute="fund_manager_resume"),
        "gender": fields.String(attribute="fund_manager_gender"),
        "return": fields.Float(attribute="nav_periodicannualizedreturn"),
        "rank": fields.Integer
    })),
    "classify": fields.String,
    "setup": fields.String,
    "bench": fields.String,
    "scale": fields.String
}


@api.resource("/<string:windcode>")
class ManagerViews(Resource):
    @marshal_with(resource_fileds)
    def get(self, windcode):
        scale = Indicators.query.with_entities(Indicators.numeric, Indicators.rpt_date).filter(Indicators.windcode == windcode, Indicators.indicator == "PRT_FUNDNETASSET_TOTAL").order_by(Indicators.rpt_date.desc()).first()
        ret = FundManager.query.filter(FundManager.windcode == windcode).one()
        ret.scale = f"{round(float(scale.numeric)/1e8,2)}亿元({scale.rpt_date.strftime('%Y-%m-%d')})"
        basic = Funds.query.filter(Funds.windcode == windcode).first()
        ret.classify = basic.classify[-1].classify
        ret.setup = basic.basic_info[-1].setup_date.strftime('%Y-%m-%d')
        ret.bench = basic.basic_info[-1].benchmark
        return ret


@api.resource("/managed/")
class ManagedViews(Resource):
    def get(self):
        latest = Classify.query.with_entities(Classify.update_date).order_by(Classify.update_date.desc()).first()[0]
        latest_fm = FundManager.query.with_entities(FundManager.update_date).order_by(FundManager.update_date.desc()).first()[0]
        name = reqparse.request.args.get("name")
        codes = FundManager.query.with_entities(FundManager.windcode).filter(FundManager.fund_fundmanager.like(f"%{name}%")).all()
        codes = list({x[0] for x in codes})
        name = BasicInfo.query.with_entities(BasicInfo.windcode, BasicInfo.sec_name).filter(BasicInfo.windcode.in_(codes)).all()
        name = list(set(name))
        name = {x[0]: x[1] for x in name}
        cls = Classify.query.with_entities(Classify.windcode, Classify.classify).filter(Classify.windcode.in_(codes), Classify.update_date == latest).all()
        cls = {x[0]: x[1] for x in cls}
        manager = FundManager.query.filter(FundManager.windcode.in_(codes), FundManager.update_date == latest_fm).all()
        manager = {x.windcode: [self.split(x.fund_predfundmanager), x.manager_info[0].nav_periodicannualizedreturn] for x in manager}
        ret = []
        for x in name.keys():
            info = {
                "windcode": x,
                "sec_name": name[x],
                "classify": cls[x],
                "serve_date": manager[x][0],
                "return": round(manager[x][1], 2)
            }
            ret.append(info)
        return ret

    def split(self, managers):
        managers = managers.split("\r\n")
        manager = None
        for x in managers:
            if "至今" in x:
                manager = x.split("(")[1][:8]
                break
        return manager
