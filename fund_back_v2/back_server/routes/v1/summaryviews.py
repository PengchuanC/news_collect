from flask_restful import Api, Resource, reqparse

from . import rest
from ...models import Classify, Funds
from .func import util, summary


api = Api(rest, prefix="/summary")


def pageparse():
    parser = reqparse.RequestParser()
    parser.add_argument("page", type=int)
    args = parser.parse_args()
    page = args["page"]
    return page


@api.resource("/")
class SummaryViews(Resource):
    def get(self):
        page = pageparse()
        latest = Classify.query.with_entities(Classify.update_date).order_by(Classify.update_date.desc()).first()[0]
        c = Classify.query.filter(Classify.update_date == latest).paginate(page, 25, False)
        page, per_page, total, items = util.zip_paginate(c)
        c = [x.to_dict() for x in items]
        date = c[0]['update_date'].strftime("%Y-%m-%d")
        c = [{"windcode": x['windcode'], "branch": x['branch'], 'classify': x['classify'],
              "update_date": x["update_date"].strftime("%Y-%m-%d")} for x in c]
        return {"date": date, "data": c, 'page': page, "total": total, "per_page": per_page}


@api.resource("/info")
class SummaryInfoViews(Resource):
    def get(self):
        update_date = Classify.query.with_entities(Classify.update_date).order_by(Classify.update_date.desc()).first()[0]
        page = pageparse()
        c = Funds.query.join(Classify).filter(Classify.update_date == update_date).paginate(page, 25, False)
        page, per_page, total, items = util.zip_paginate(c)
        ret = [{
            "windcode": x.windcode, "classify": x.classify[-1].classify, "sec_name": x.basic_info[-1].sec_name,
            "benchmark": x.basic_info[-1].benchmark, "setupdate": x.basic_info[-1].setup_date.strftime("%Y-%m-%d"),
            "branch": x.classify[-1].branch
                } for x in items]
        return {"data": ret, "page": page, "per_page": per_page, "total": total}


@api.resource("/bc")
class BranchClassifyViews(Resource):
    def get(self):
        ret = summary.summarise()
        return ret
