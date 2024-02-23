from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from sqlite_db import get_staff_names

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Управление проектами').add('Управление сотрудниками')



catalog_list = ReplyKeyboardMarkup(resize_keyboard=True)
catalog_list.add('Digitals').add('Education').add('Commerce')



project_manager = ReplyKeyboardMarkup(resize_keyboard=True)
project_manager.add('Посмотреть проекты').add('Изменить проект').add('Добавить проект').add('Удалить проект').add('Главное меню')

project_edit_options = ReplyKeyboardMarkup(resize_keyboard=True)
project_edit_options.add('Название').add('Описание').add('Участников').add('Завершенность').add('Дедлайн').add('Отменить')





staff_manager = ReplyKeyboardMarkup(resize_keyboard=True)
staff_manager.add('Посмотреть сотрудников').add('Добавить сотрудника').add('Удалить сотрудника').add('Главное меню')


user_kb = ReplyKeyboardMarkup(resize_keyboard=True)
user_kb.add('Посмотреть проекты').add('Посмотреть сотрудников')


departmentsWithBack = ReplyKeyboardMarkup(resize_keyboard=True)
departmentsWithBack.add('Digitals').add('Education').add('Commerce').add('Назад')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отменить')

async def create_staff_keyboard():
    staff_names = await get_staff_names()
    staff_list = ReplyKeyboardMarkup(resize_keyboard=True)

    for staff_name in staff_names:
        staff_list.add(KeyboardButton(staff_name))
    staff_list.add('Завершить')
    return staff_list
