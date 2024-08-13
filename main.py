import asyncio
import os
import time
from telebot import types
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import redis.asyncio as redis
from database import User
import texts


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = AsyncTeleBot(TELEGRAM_TOKEN)

r = redis.Redis(host='localhost', port=6379, db=0)
SEVEN_DAYS = 604800


@bot.message_handler(commands=['start'])
async def welcome(message):
    try:
        User.create(
            tg_username=message.from_user.username,
            tg_id=message.from_user.id,
        )
        expiration_time = int(time.time()) + SEVEN_DAYS
        await r.set(f"user:{message.from_user.id}:notify_time", expiration_time)
    except Exception as e:
        print(e)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    login_button = types.InlineKeyboardButton(text="Создать личный кабинет", url='https://academy.bodycoach.pro/buy/178')
    keyboard.add(login_button)
    await bot.send_photo(
        message.chat.id,
        photo=open('img/img_hello.png', 'rb'),
        caption=texts.hello_text,
        reply_markup=keyboard,
        )

    lesson_keyboard = types.InlineKeyboardMarkup(row_width=1)
    lesson_button = types.InlineKeyboardButton(text='Смотреть первый урок', url='https://academy.bodycoach.pro/training/view/osnovy-nutriciologii/lesson/1-nauka-o-pitanii-cheloveka-neobhodimye-umeniya-v-rabote-nutriciologa-')
    next_lesson_button = types.InlineKeyboardButton(text='Смотреть следующий урок', callback_data='lesson2')
    lesson_keyboard.add(lesson_button, next_lesson_button)
    await bot.send_photo(
        message.chat.id,
        photo=open('img/img_lesson1.png', 'rb'),
        caption=texts.lesson1_text,
        reply_markup=lesson_keyboard,
        )


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    if call.data == 'lesson2':
        application_keyboard = types.InlineKeyboardMarkup(row_width=1)
        nutrition_button = types.InlineKeyboardButton(text='Смотреть второй урок', url='https://academy.bodycoach.pro/training/view/osnovy-nutriciologii/lesson/2-nacionalnye-rekomendacii-po-pitaniyu-razlichnyh-stran-')
        ap_button = types.InlineKeyboardButton(text='Смотреть следующий урок', callback_data='lesson3')
        application_keyboard.add(nutrition_button, ap_button)
        await bot.send_photo(
            call.message.chat.id,
            photo=open('img/img_lesson2.png', 'rb'),
            caption=texts.lesson2_text,
            reply_markup=application_keyboard,
        )

    if call.data == 'lesson3':
        application_keyboard = types.InlineKeyboardMarkup(row_width=1)
        nutrition_button = types.InlineKeyboardButton(text='Смотреть третий урок', url='https://academy.bodycoach.pro/training/view/osnovy-nutriciologii/lesson/3-chto-vliyaet-na-massu-tela-')
        ap_button = types.InlineKeyboardButton(text='Смотреть следующий урок', callback_data='lesson4')
        application_keyboard.add(nutrition_button, ap_button)
        await bot.send_photo(
            call.message.chat.id,
            photo=open('img/img_lesson3.png', 'rb'),
            caption=texts.lesson3_text,
            reply_markup=application_keyboard,
        )

    if call.data == 'lesson4':
        application_keyboard = types.InlineKeyboardMarkup(row_width=1)
        nutrition_button = types.InlineKeyboardButton(text='Смотреть четвертый урок', url='https://academy.bodycoach.pro/training/view/osnovy-nutriciologii/lesson/4-son-i-fizicheskaya-aktivnost-vaghnye-aspekty-v-rabote-nutriciologa-')
        ap_button = types.InlineKeyboardButton(text='Получить сертификат', url='https://academy.bodycoach.pro/training/view/osnovy-nutriciologii/lesson/kak-poluchit-sertifikat')
        application_keyboard.add(nutrition_button, ap_button)
        await bot.send_photo(
            call.message.chat.id,
            photo=open('img/img_lesson4.png', 'rb'),
            caption=texts.lesson4_text,
            reply_markup=application_keyboard,
        )
        expiration_time = int(time.time()) + 86400
        await r.set(f"user:{call.message.chat.id}:next_lesson_time", expiration_time)


async def check_next_lesson():
    while True:
        async for key in r.scan_iter("user:*:next_lesson_time"):
            key_str = key.decode('utf-8')
            next_lesson_time = int(await r.get(key))
            current_time = int(time.time())
            if current_time >= next_lesson_time:
                chat_id = key_str.split(":")[1]

                application_keyboard = types.InlineKeyboardMarkup(row_width=1)
                nutrition_button = types.InlineKeyboardButton(text='Общая нутрициология', url='https://academy.bodycoach.pro/buy/98')
                ap_button = types.InlineKeyboardButton(text='Нутрициология и адаптивное питание', url='https://academy.bodycoach.pro/buy/99')
                review_button = types.InlineKeyboardButton(text='Читать отзывы', url='https://vk.com/bodycoachschool?w=wall-31941952_10669')

                second_level_keyboard = types.InlineKeyboardMarkup(row_width=1)
                second_level_button = types.InlineKeyboardButton(text='Смотреть 2 урока', url='https://academy.bodycoach.pro/training/view/osnovy-nutriciologii')
                next_button = types.InlineKeyboardButton(text='Записаться на обучение', url='https://t.me/BodyCoach_bot')
                application_keyboard.add(nutrition_button, ap_button, review_button)
                second_level_keyboard.add(second_level_button, next_button)

                await bot.send_message(
                    chat_id,
                    text=texts.application_text,
                    reply_markup=application_keyboard,
                )
                await bot.send_message(
                    chat_id,
                    text=texts.second_level_text,
                    reply_markup=second_level_keyboard,
                )

                await r.delete(key)
        await asyncio.sleep(3600)  # Проверяем каждый час


async def check_notifications():
    while True:
        async for key in r.scan_iter("user:*:notify_time"):
            key_str = key.decode('utf-8')
            notify_time = int(await r.get(key))
            current_time = int(time.time())
            if current_time >= notify_time:
                user_id = key_str.split(":")[1]
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                save_button = types.InlineKeyboardButton(text='Оставить записи', url='https://academy.bodycoach.pro/buy/2')
                keyboard.add(save_button)
                await bot.send_message(
                    user_id,
                    text=texts.save_videos_text,
                    reply_markup=keyboard,
                    )
                await r.delete(key)
        await asyncio.sleep(3600)


async def main_loop():
    asyncio.create_task(check_next_lesson())
    asyncio.create_task(check_notifications())
    while True:
        try:
            await bot.infinity_polling(timeout=10, request_timeout=20)
        except Exception:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main_loop())
