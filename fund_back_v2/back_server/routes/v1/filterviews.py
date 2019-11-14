from flask_restful import Api, Resource, request

from . import rest

from .func import filters

api = Api(rest, prefix="/filter")


@api.resource("/filter", methods=["POST"])
class FilterViews(Resource):
    def post(self):
        data = request.json
        funds = filters.execute_basic_filter(data)
        if isinstance(funds, int):
            return {"msg": "invalid request"}
        return {"data": list(funds)}


@api.resource("/advance_filter", methods=["POST"])
class AdvanceViews(Resource):
    def post(self):
        data = request.json
        funds = data['funds']
        f = data["filter"]
        funds = filters.execute_advance_filter(funds, f)
        return {"data": list(funds)}


@api.resource("/info", methods=["GET", "POST"])
class FilterBasicInfoViews(Resource):
    def post(self):
        data = request.json
        funds = data["funds"]
        page = data["page"]
        _filters = data["filter"]
        data, page, per_page, total = filters.fund_details(funds, _filters, page)
        return {"data": data, "page": page, "total": total, "per_page": per_page}


@api.resource("/info/result", methods=["POST"])
class InfoResultViews(Resource):
    def post(self):
        data = request.json
        funds = data["funds"]
        _filters = data["filter"]
        filters.fund_details_to_excel(funds, _filters)
        return {'message': "OK", "url": "api/v1/filter/info/results"}
