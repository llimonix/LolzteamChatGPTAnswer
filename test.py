import json
import requests
import time
from loguru import logger

from tab2 import ThabAi

thab_ai = ThabAi()
token_lolz = "ТУТ ТВОЙ ТОКЕН"
forum_id = 585 # Если не знаете где взять нужный для вас раздел, напишите в комментариях в теме. 876 - тестовый раздел. 585 - тематические вопросы
headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {token_lolz}',
}

# Глобальный список тем, где бот отвечал
threads_ready = []
first_start = True

def ThabAIGen(text_lolz):
    logger.info('Получаем ответ от ThabAI')
    text = thab_ai.get_response(text_lolz)
    logger.success('Ответ от ThabAI получен')
    return text


def get_thread_ids(params):
    response = requests.get('https://api.zelenka.guru/threads', params=params, headers=headers)
    threads = response.json().get('threads', [])
    thread_ids = [thread['thread_id'] for thread in threads]
    return thread_ids


def process_question(thread_id):
    res = requests.get(f'https://api.zelenka.guru/threads/{thread_id}', headers=headers)
    thread = res.json().get('thread')

    if thread:
        thread_title = thread['thread_title']
        thread_text = thread['first_post']['post_body_plain_text']
        create_username = thread['creator_username']
        create_user_id = thread['creator_user_id']
        text_lolz = f'{thread_title} {thread_text}'
        logger.info(f'Заголовок темы: {thread_title} от {create_username}')
        answer_bot = ThabAIGen(text_lolz)
        time.sleep(3)

        params = {'thread_id': thread_id}
        data = {
            'post_body': f'[USER={create_user_id}]@{create_username}[/USER], {answer_bot} \n\nОтвет был отправлен ботом. Я временная замена для СhatGPT форума. Всегда к вашим услугам'}

        try:
            res = requests.post('https://api.zelenka.guru/posts', params=params, headers=headers, data=data)
            status = res.json().get('post')
            if status is not None:
                logger.success('Ответ на вопрос успешно отправлен')
            else:
                logger.error('Ответ на вопрос не был отправлен')
        except:
            logger.error('Ошибка отправки сообщения')


def CheckNewQuestion():
    global first_start
    global threads_ready

    logger.info('Получаю ID тем и начинаю ждать новые...')

    while True:
        if first_start:
            params = {
                'forum_id': f'{forum_id}',
                'order': 'thread_create_date_reverse',
                'limit': '20'
            }
            threads_ready = get_thread_ids(params)
            first_start = False
            logger.info('Первое вхождение')
        else:
            params = {
                'forum_id': f'{forum_id}',
                'order': 'thread_create_date_reverse',
                'limit': '10'
            }
            try:
                thread_ids_new = get_thread_ids(params)
            except Exception as e:
                time.sleep(30)
                logger.error(f'Ошибка: {e}')
                thread_ids_new = get_thread_ids(params)

            new_threads = [x for x in thread_ids_new if x not in threads_ready]
            threads_count = len(new_threads)
            logger.info(f'Количество новых тем: {threads_count}')

            if threads_count != 0:
                time.sleep(3)
                for thread_id in new_threads:
                    logger.info(f'Начинаю работать с темой: {thread_id}')
                    threads_ready.append(thread_id)
                    process_question(thread_id)

        time.sleep(10)


if __name__ == '__main__':
    while True:
        try:
            CheckNewQuestion()
        except Exception as e:
            logger.error(f'Ошибка: {e}')

