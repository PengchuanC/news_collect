import click

from app.scheduler import schedule, schedule_special, schedule_special_hibor, schedule_special_search_api
from app.config import website


@click.group()
def run():
    pass


@run.command()
def collect_all():
    for name in website.keys():
        schedule(name)
    schedule_special()
    schedule_special_search_api()
    schedule_special_hibor()


if __name__ == '__main__':
    run()
