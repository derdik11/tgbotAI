from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Iphone 11'),KeyboardButton(text='Iphone 12')],
    [KeyboardButton(text='Iphone 13') ,KeyboardButton(text='Iphone 14')], 
    [KeyboardButton(text='Iphone 15')],
    [KeyboardButton(text='Go Back')]

],
                            resize_keyboard=True,
                            input_field_placeholder='Pick a button!')

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Catalog', callback_data='catalog')]
    
    
])

appl_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Apple devices', url= 'https://nsv.by/brands/apple/')],
    [InlineKeyboardButton(text='Go Back', callback_data='Back')]
])

phones = ['Apple', 'Samsung', 'Honor']

async def inline_phones():
    keybort = InlineKeyboardBuilder()
    for phone in phones:
        keybort.add(InlineKeyboardButton(text=phone, callback_data=phone))
    return keybort.adjust(1).as_markup()