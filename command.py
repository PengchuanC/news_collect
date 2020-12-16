import click
import os

from concurrent.futures import ThreadPoolExecutor, wait
from app.scheduler import schedule, schedule_special, schedule_special_hibor, schedule_special_search_api
from app.config import website


@click.group()
def run():
    pass


def normal():
    for name in website.keys():
        try:
            schedule(name)
        except Exception as e:
            print(e)


@run.command()
def collect_all():
    for name in website.keys():
        try:
            schedule(name)
        except Exception as e:
            print(e)
    try:
        schedule_special()
    except Exception as e:
        print(e)
    try:
        schedule_special_search_api()
    except Exception as e:
        print(e)
    try:
        schedule_special_hibor()
    except Exception as e:
        print(e)


@run.command()
def collect_all_async():
    pool = ThreadPoolExecutor(4)
    tasks = []
    for t in (normal, schedule_special, schedule_special_hibor, schedule_special_search_api):
        thread = pool.submit(t)
        tasks.append(thread)
    wait(tasks, 60*20)
    os._exit(0)


if __name__ == '__main__':
    run()
