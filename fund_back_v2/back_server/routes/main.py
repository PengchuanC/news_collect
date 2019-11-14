import os
from flask_restful import Api, Resource
from flask import make_response, send_file

from . import main


api = Api(main)


@api.resource("/")
class Index(Resource):
    def get(self):
        return {"data": "fund_filter system root"}


@main.route("/api/v1/filter/info/results", methods=["GET"])
def fund_filter_basic_info_export2():
    file = os.path.abspath("./back_server/static/筛选结果.xlsx")
    response = make_response(send_file(file, as_attachment=True, attachment_filename="筛选结果.xlsx"), 200)
    response.headers["Content-Disposition"] = "attachment;filename=results.xlsx;"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response