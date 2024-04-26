import requests

request_everything = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5', 'url': 'https://newsapi.org/v2/everything',
                      'q': 'яндекс',
                      'language': 'ru', 'sortBy': 'popularity'}

request_top_headlines = {'apiKey': '162e6651da2c4734b2cfa2d940a47cc5', 'url': 'https://newsapi.org/v2/top-headlines',
                         'country': 'ru', 'category': 'business'}


def everything(params):
    req = requests.get(f'{params['url']}?'
                       f'apiKey={params['apiKey']}&'
                       f'q={params['q']}&'
                       f'language={params['language']}&'
                       f'sortBy={params['sortBy']}')
    json = req.json()
    return json


def top_headlines(params):
    req = requests.get(f'{params['url']}?'
                       f'apiKey={params['apiKey']}&'
                       f'country={params['country']}&'
                       f'category={params['category']}')
    json = req.json()
    return json
