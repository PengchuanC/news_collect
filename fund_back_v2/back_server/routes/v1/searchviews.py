from flask_restful import Api, Resource, reqparse
from sqlalchemy import or_


from . import rest
from ...models import BasicInfo, db


api = Api(rest, prefix="/search")


@api.resource("/fundlist")
class FundListViews(Resource):
    def get(self):
        bi = BasicInfo
        ret = bi.query.with_entities(bi.windcode, bi.sec_name).all()
        return ret

    def post(self):
        bi = BasicInfo
        parser = reqparse.RequestParser()
        parser.add_argument("search", type=str)
        args = parser.parse_args()
        search = f'%{args["search"]}%'
        ret = bi.query.with_entities(db.func.distinct(bi.windcode), bi.sec_name).filter(or_(bi.sec_name.ilike(search), bi.windcode.ilike(search))).all()
        return ret[:10] if len(ret) > 10 else ret
