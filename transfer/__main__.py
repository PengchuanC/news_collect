from transfer import api


news = api.news_from_remote()
api.news_to_local(news)

news = api.news_from_local()
api.news_to_remote(news)
