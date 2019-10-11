import abc


class SpecialCollector(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, keyword=None, page=None):
        self.keyword = keyword
        self.page = page

    @abc.abstractmethod
    def format_url(self):
        pass

    @abc.abstractmethod
    def collect(self):
        pass
