import os
from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
sessionStorage = {}
cities = {
    'москва': ['', ''],
    'нью-йорк': ['', ''],
    'париж': ['', '']
}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)
    logging.info('Response: %r', response)
    return jsonify(response)


def get_first_name(req) -> None | str:
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)
    return None


def get_city(req) -> None | str:
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)
    return None


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'firstname': None,
        }
        return

    if sessionStorage[user_id]['firstname'] is None:
        firstname = get_first_name(req)
        if firstname is None:
            res['response']['text'] = 'Не расслышала имя. Повторите пожалуйста!'
        else:
            sessionStorage[user_id]['firstname'] = firstname
            res['response']['text'] \
                = f'Приятно познакомится, {firstname.title()}. Я - Алиса. Какой город хочешь увидеть?'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities.keys()
            ]
    else:
        city = get_city(req)
        if city is cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю.'
            res['response']['card']['image_id'] = random.choice(cities[city])
            res['response']['text'] = 'Я угадала!'
        else:
            res['response']['text'] = 'Перевый раз слышу об этом городе. Попробуй ещё раз!'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# https://flask-2--semenovtv.replit.app
