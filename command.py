import click

from app.scheduler import schedule, schedule_special, schedule_special_hibor, schedule_special_search_api
from app.config import website


@click.group()
def run():
    pass


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


if __name__ == '__main__':
    run()
