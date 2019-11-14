from flask import Blueprint
rest = Blueprint("rest", __name__)

from .test import *
from .newsviews import *
from .searchviews import *
from .infoviews import *
from .managerviews import *
from .summaryviews import *
from .portfolioviews import *
from .plotviews import *
from .filterviews import *
