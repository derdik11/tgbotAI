import os
import requests
import logging
from aiogram import F, Router, Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

from notion_client import Client

import openai

import hand.key as k

import openai

from config import OpenToken

logging.basicConfig(level=logging.INFO)

openai.api_key = OpenToken

notion = Client(auth="notion_id")

database_id = "database_id"

r = Router()

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()


@r.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello!, write /help to see what this bot can do', reply_markup=k.settings)

@r.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('The list of phones: ',reply_markup=await k.inline_phones())

@r.callback_query(F.data == 'Back')
async def back(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('The list of phones: ',reply_markup=k.settings)


@r.callback_query(F.data == 'Apple')
async def apple(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('The webiste for your future Apple device', reply_markup=k.appl_button)

@r.message(Command('help'))
async def get_command(message: Message):
    await message.answer('This bot can help you to find some information, just press the button', reply_markup=k.main)

@r.message(F.text == 'First Button')
async def first_button(message: Message):
    with open('text.txt', 'r') as file:
        first_line = file.readline().strip() 

    await message.reply(first_line)

@r.message(F.text == 'Second Button')
async def second_button(message: Message):
    with open('text.txt', 'r') as file:
        lines = file.readlines()
        second_line = lines[1].strip() if len(lines) > 1 else print('No second line in file') 

    await message.reply(second_line)


@r.message(F.text == 'Go Back')
async def back_button(message: Message):
    await message.reply('Type /start to go back')

@r.message(F.text)
async def chatgpt_response2(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info(f"Current state: {current_state}")

    if current_state is None:
        user_message = message.text

        response = notion.databases.query(database_id=database_id)
        results = response.get('results', [])
        notion_data = []
        for page in results:
            title = page['properties']['Apple']['title'][0]['text']['content']
            price = page['properties']['price']['number']
            image_url = page['properties']['pict']['files'][0]['file']['url']
            web_url = page['properties']['web']['url']
            notion_data.append({
                "title": title,
                "price": price,
                "pict": image_url,
                "web": web_url
            })

        system_message = f"""
        Ты - опытный консультант, готовый помочь клиентам с выбором телефонов, всегда должен помнить про какой телефон идет разговор. Твоя цель - обеспечить клиентов всей необходимой информацией для принятия решения, используя данные из базы данных Notion. Не надо никаким образом выделять какие-то текста в сообщениях, отправляй их без выделения, например(не используй *)
        Определение модели: Если клиент упоминает конкретную модель, чат-бот должен сразу предоставить информацию о данной модели.
        Описание модели: Предоставить основные характеристики и функции модели без необходимости уточнять повторно.
        Уточнение вопросов: Если клиент задает общие вопросы, предоставить подробные ответы, не запрашивая модель снова.
        При упоминании конкретной модели сразу предоставлять информацию о ней.
        Не переспрашивать про модель телефона, если она уже была указана.
        Описывать характеристики и функции указанной модели подробно.
        Если клиент задает общие вопросы (например, про стоимость или особенности), предоставлять ответы без дополнительных уточнений.
        Используй эти поля для фильтрации данных:
        Ты должен понимать и спрашивать, когда покупатель готов купить телефон и узнавать его данные: имя, фамилию и номер телефона поочередно, ты должен задать вопрос готов ли покупатель к покупке или что-то типо этого, 
        ты должен спросить готов или нет, после положительного ответа(да) запроси имя, только после овтета пользователя запрашивать его имя и данные.
        Ты должен понимать последовательность всех сообщений, анализировать свои сообщения и сообщения покупателя, делать выводы и понимать, что он хочет, не переспрашивая каких-то вопросов. 
        Например: вы общаетесь про какой-то телефон, ты все время должен понимать про какой телефон вы общаетесь, не переспрашивая этого. Ты должен анализировать предыдущеей сообщение и когда покупатель пишет этот или эти телефоны, должен понимать про какой телефон идет речь
        Не отправляй фотографию ссылкой, пиши больше информации словами, ссылкой фотографию отправлять не надо
        инструкция: 
        "Apple": текстовое поле
        "price": числовое поле
        "pict": файл
        "web": url
        По числовым полям искать используя диапазон.
        Вот данные из базы данных Notion:\n{notion_data}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=8000
        )
        if any(phrase in user_message.lower() for phrase in ["все телефоны", "весь товар", "список телефонов", "список товара"]):
            for row in notion_data:
                caption = (f"**{row['title']}**\n"
                        f"Цена: {row['price']} $\n"
                        f"[Подробнее]({row['web']})")

            
                await message.answer_photo(photo=row['pict'], caption=caption, parse_mode='Markdown')
            await message.answer("Вот список телефонов, которые есть в наличие, если у вас есть какие-то вопросы, задавайте их мне!")

        else:

            bot_response = response.choices[0].message['content'].strip()
            await message.answer(bot_response)

        if any(phrase in user_message.lower() for phrase in ["да", "готов купить", "готов оформить заказ", "хочу купить", "оформить заказ", "готов сделать покупку"]):
            
            await state.set_state(OrderStates.waiting_for_name)
            logging.info("Set state to waiting_for_name")
    elif current_state == OrderStates.waiting_for_name.state:
        await process_name(message, state)
    elif current_state == OrderStates.waiting_for_surname.state:
        await process_surname(message, state)
    elif current_state == OrderStates.waiting_for_phone.state:
        await process_phone(message, state)

async def process_name(message: Message, state: FSMContext):
    logging.info(f"Processing name: {message.text}")
    await state.update_data(name=message.text)
    await message.answer("Теперь укажите вашу фамилию.")
    await state.set_state(OrderStates.waiting_for_surname)
    logging.info("Set state to waiting_for_surname")

async def process_surname(message: Message, state: FSMContext):
    logging.info(f"Processing surname: {message.text}")
    await state.update_data(surname=message.text)
    await message.answer("Пожалуйста, укажите ваш номер телефона.")
    await state.set_state(OrderStates.waiting_for_phone)
    logging.info("Set state to waiting_for_phone")

async def process_phone(message: Message, state: FSMContext):
    logging.info(f"Processing phone: {message.text}")
    user_data = await state.get_data()
    name = user_data['name']
    surname = user_data['surname']
    phone = message.text

    with open('text.txt', 'a', encoding='utf-8') as file:
        file.write(f"Имя: {name}, Фамилия: {surname}, Телефон: {phone}\n")

    await message.answer("Спасибо за предоставленные данные! Я свяжусь с вами в ближайшее время для завершения оформления заказа. Если у вас возникнут дополнительные вопросы, не стесняйтесь обращаться. Хорошего дня!")
    await state.clear()
    logging.info("Order completed and state cleared")
    
