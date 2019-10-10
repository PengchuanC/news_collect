import abc


class Collector(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, section, path=None, page=None):
        self.section = section
        self.path = path
        self.page = page

    @abc.abstractmethod
    def format_url(self):
        pass

    @abc.abstractmethod
    def collect(self):
        pass
