from flask_restful import Api, Resource, fields, marshal_with, reqparse

from . import rest

from ...models import FundPerformance, db, Style
from ...models import BasicInfo

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


@fs.resource("/")
class Performance(Resource):

    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument("windcode", type=str)
        args = parse.parse_args()
        windcode = args.get("windcode")
        fp = FundPerformance
        sec_name = BasicInfo.query.with_entities(BasicInfo.sec_name).filter_by(windcode=windcode).first()[0]
        max_update_date = db.session.query(db.func.max(fp.update_date)).filter(fp.windcode == windcode).one()[0]
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
        parser = reqparse.RequestParser()
        parser.add_argument("windcode", type=str)
        args = parser.parse_args()
        windcode = args.get("windcode")

        ret = Style.query.filter(Style.windcode == windcode).all()
        return ret
