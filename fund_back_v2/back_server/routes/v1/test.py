from flask_restful import Api, Resource

from . import rest
from ...models import BasicInfo, db, Funds


api = Api(rest, prefix="/test")


@api.resource("/basic")
class BasicInformationViews(Resource):
    def get(self):
        ret = BasicInfo.query.filter(BasicInfo.windcode == "000009.OF").all()
        print(ret[0].to_dict())
        return
