from functools import lru_cache

from ....models import Indicators, IndicatorsForPlot, Classify, db


@lru_cache(20)
def latest_update_date():
    ifp = IndicatorsForPlot
    _latest_update_date = db.session.query(db.func.max(ifp.UPDATE_DATE)).one()[0]
    return _latest_update_date


def summary():
    """基金分类总结"""
    _latest_update_date = latest_update_date()
    total_count = db.session.query(db.func.count(db.func.distinct(Classify.windcode))).filter(
        Classify.update_date == _latest_update_date).one()
    total_count = total_count[0]
    branch = db.session.query(db.func.distinct(Classify.branch)).filter(
        Classify.update_date == _latest_update_date).all()
    branch = [x[0] for x in branch]

    open_fund = {"name": "公募基金", "value": total_count, "children": []}
    for bran in branch:
        bran_count = db.session.query(db.func.count(Classify.classify)).filter(Classify.branch == bran,
                                                                               Classify.update_date == _latest_update_date).one()
        bran_count = bran_count[0]
        classify = db.session.query(db.func.distinct(Classify.classify)).filter(Classify.branch == bran,
                                                                                Classify.update_date == _latest_update_date).all()
        classify = [x[0] for x in classify]
        branch_classify = {"name": bran, "value": bran_count, "children": []}
        for cla in classify:
            cla_count = db.session.query(db.func.count(Classify.windcode)).filter(
                Classify.branch == bran, Classify.classify == cla, Classify.update_date == _latest_update_date
            ).one()
            cla_count = cla_count[0]
            _classify = {"name": cla, "value": cla_count}
            branch_classify["children"].append(_classify)
        open_fund["children"].append(branch_classify)
    return open_fund


def summarise():
    """基金分类概括"""
    cls = Classify
    ins = Indicators
    latest_cls = cls.query.with_entities(cls.update_date).order_by(cls.update_date.desc()).limit(1).first()[0]
    latest_ins = ins.query.with_entities(ins.update_date).order_by(ins.update_date.desc()).limit(1).first()[0]
    latest_rpt = \
    ins.query.with_entities(ins.rpt_date).order_by(ins.update_date.desc(), ins.rpt_date.desc()).limit(1).first()[0]

    data = db.session.query(cls.windcode, cls.branch, cls.classify, ins.numeric).filter(cls.update_date == latest_cls,
                                                                                        ins.update_date == latest_ins,
                                                                                        ins.rpt_date == latest_rpt,
                                                                                        ins.indicator == "NETASSET_TOTAL",
                                                                                        cls.windcode == ins.windcode).all()
    total = {x[0]: float(x[-1]) if x[-1] else 0 for x in data}
    t_c, t_s = len(total.keys()), format(round(sum(total.values()) / 1e8, 0), '0,.0f')

    b_ret, c_ret = [], []
    branch = set([x[1] for x in data])
    for b in branch:
        classify = set(x[2] for x in data if x[1] == b)
        b_data = {x[0]: float(x[-1]) if x[-1] else 0 for x in data if x[1] == b}
        b_c, b_s = len(b_data.keys()), format(round(sum(b_data.values()) / 1e8, 0), '0,.0f')
        children = []
        b_ret.append({"branch": b, 'count': b_c, 'scale': b_s, "children": children})
        for c in classify:
            c_data = {x[0]: float(x[-1]) if x[-1] else 0 for x in data if x[1] == b and x[2] == c}
            c_c, c_s = len(c_data.keys()), format(round(sum(c_data.values()) / 1e8, 0), '0,.0f')
            children.append({"branch": b, "classify": c, "count": c_c, "scale": c_s})
    return {"total": {"count": t_c, "scale": t_s}, "branch": b_ret}
