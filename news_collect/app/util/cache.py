import os
import shelve

from datetime import date
from functools import wraps

base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "data")


class LocalStorage(object):
    def __init__(self):
        self.file = os.path.join(data_dir, "storage")

    def dump(self, name, data):
        with shelve.open(self.file) as s:
            if name in s.keys():
                raise AttributeError(f"object <{name}> is already in cache, you may delete or update it.")
            s[name] = data

    def load(self, name):
        with shelve.open(self.file) as s:
            if name not in s.keys():
                raise AttributeError(f"object <{name}> is not in cache, you may dump it.")
            data = s.get(name)
        return data

    def update(self, name, data):
        with shelve.open(self.file) as s:
            if name not in s.keys():
                raise AttributeError(f"object <{name}> is not in cache, you may dump it.")
            s[name] = data

    def delete(self, name):
        with shelve.open(self.file) as s:
            if name not in s.keys():
                raise AttributeError(f"object <{name}> is not in cache, you cant delete it.")
            data = s.pop(name)
        return data

    def preview(self):
        with shelve.open(self.file) as s:
            keys = list(s.keys())
        return keys

    def insert(self, name, data):
        with shelve.open(self.file) as s:
            s[name] = data


class Cache(object):
    def __init__(self, name, func):
        self.flag = date.today().strftime("%Y-%m-%d")
        self.name = name
        self.func = func
        self.ls = LocalStorage()

    def check_flag(self, flag=date.today().strftime("%Y-%m-%d")):
        if flag == self.flag:
            return True
        else:
            self.flag = flag
        return False

    def init_cache(self):
        data = self.func()
        self.ls.insert(self.name, data)
        return data

    def cache(self):
        if self.check_flag():
            try:
                data = self.ls.load(self.name)
            except AttributeError:
                data = self.init_cache()
        else:
            data = self.init_cache()
        return data


if __name__ == '__main__':
    ls = LocalStorage()
    ls.dump("test", ["test"])
