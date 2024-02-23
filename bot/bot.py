from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import keyboards as kb
import sqlite_db as db
from datetime import datetime




storage = MemoryStorage()

bot = Bot('Токен твоего бота')
dp = Dispatcher(bot=bot, storage=storage)
logging_middleware = LoggingMiddleware()
dp.middleware.setup(logging_middleware)

ADMIN_LIST = ['1013735330']

def admin_access(func):
    async def wrapper(message: types.Message):
        user_id = str(message.from_user.id)
        if user_id in ADMIN_LIST:
            await func(message)
        else:
            await message.answer('У вас нету доступа')
    return wrapper


async def on_startup(_):
    await db.db_start()
    print('Бот запущен!')


class NewStaff(StatesGroup):
    full_name = State()
    about = State()


class NewOrder(StatesGroup):
    name = State()
    description = State()
    performers = State()
    department = State()
    deadline = State()


class EditProject(StatesGroup):
    GET_PROJECT_ID = State()
    EDITING_OPTIONS = State()
    EDITING_FIELD = State()


class DeleteProj(StatesGroup):
    GET_ID = State()


class DeleteStaff(StatesGroup):
    GET_ID = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAEDZuVlx6DBQry15wn4Z03CwXTln4sWewAC2A8AAkjyYEsV-8TaeHRrmDQE')
    await message.answer(f'{message.from_user.first_name}, добро пожаловать в Elif!',
                         reply_markup=kb.main)


@dp.message_handler(commands=['id'])
async def cmd_id(message: types.Message):
    await message.answer(f'ID: {message.from_user.id}')


@dp.message_handler(text='Управление проектами')
@admin_access
async def project_managing(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAEDattlyK_BbrIT3elv2Hika5n4Kk62tQACLA0AArs76EuqM6J0TSMuQTQE', reply_markup=kb.project_manager)
@dp.message_handler(text='Управление сотрудниками')
@admin_access
async def staff_managing(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAEDat9lyLA3qIff8sFa1iz47BR6mDvTegACJg4AAvW6EEiEWDQIzqqeEzQE', reply_markup=kb.staff_manager)


@dp.message_handler(text=['Посмотреть проекты'])
@admin_access
async def digital(message: types.Message):
    await message.answer('Выберите отдел', reply_markup=kb.departmentsWithBack)


@dp.message_handler(text='Добавить сотрудника')
@admin_access
async def add_staff(message: types.Message):
    await message.answer('Напишите полное имя сотрудника')
    await NewStaff.full_name.set()


@dp.message_handler(state=NewStaff.full_name)
async def add_staff_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text
    await message.answer('Напишите специальность сотрудника')
    await NewStaff.next()


@dp.message_handler(state=NewStaff.about)
async def add_staff_about(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['about'] = message.text
    await db.add_staff(state)
    await message.answer('Сотрудник успешно добавлен', reply_markup=kb.staff_manager)
    await state.finish()


@dp.message_handler(text='Добавить проект')
@admin_access
async def add_project(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAEDkM9l0bMrRkkC3XN_yzX2WwtB2hjX-wAC7goAAp2hYUuW93rCAubsUDQE')
    await message.answer('Напишите название проекта')
    await NewOrder.name.set()


@dp.message_handler(state=NewOrder.name)
async def add_project_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Напишите описание проекта')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.description)
async def add_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    staff_kb = await kb.create_staff_keyboard()
    await message.answer('Напишите участников проекта', reply_markup=staff_kb)
    await NewOrder.next()


@dp.message_handler(state=NewOrder.performers)
async def add_performers(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if 'performers' not in data:
            data['performers'] = ''
        if message.text == 'Завершить':
            await message.answer('Выберите отдел проекта', reply_markup=kb.catalog_list)
            await NewOrder.next()
            return

        if data['performers']:
            data['performers'] += ", "
        data['performers'] += message.text


@dp.message_handler(state=NewOrder.department)
async def add_performers(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['department'] = message.text
    await message.answer('Напишите дедлайн проекта в формате ГГ-ММ-ДД')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.deadline)
async def add_deadline(message: types.Message, state: FSMContext):
    try:
        date_obj = datetime.strptime(message.text, '%Y-%m-%d')

        async with state.proxy() as data:
            data['complete'] = '0'
            data['deadline'] = date_obj

        await db.add_project(state)
        await message.answer('Проект успешно добавлен', reply_markup=kb.project_manager)
        await state.finish()

    except ValueError:
        await message.answer('Вы ввели неправильный формат даты. Введите в формате ГГ-ММ-ДД')



@dp.message_handler(text=['Digitals', 'Education', 'Commerce'])
@admin_access
async def show_projects(message: types.Message):
    await db.show_projects(message)


@dp.message_handler(text='Посмотреть сотрудников')
@admin_access
async def show_staff(message: types.Message):
    await db.show_staff(message)


@dp.message_handler(text='Изменить проект')
@admin_access
async def change_project(message: types.Message):
    await message.answer('Введите ID проекта, который хотите изменить')
    await EditProject.GET_PROJECT_ID.set()


@dp.message_handler(state=EditProject.GET_PROJECT_ID)
async def process_project_id(message: types.Message, state: FSMContext):
    project_id = message.text
    if await db.check_project_exists(project_id):
        await state.update_data(project_id=project_id)
        await message.answer('Выберите опцию для изменения', reply_markup=kb.project_edit_options)
        await EditProject.EDITING_OPTIONS.set()
    else:
        await message.answer('Проект с указанным ID не найден')


@dp.message_handler(state=EditProject.EDITING_OPTIONS)
async def process_editing_options(message: types.Message, state: FSMContext):
    option = message.text
    option_to_field = {
        'Название': 'name',
        'Описание': 'description',
        'Участников': 'performers',
        'Завершенность': 'complete',
        'Дедлайн': 'deadline'
    }
    staff_kb = await kb.create_staff_keyboard()

    if option in option_to_field:
        field = option_to_field[option]
        await state.update_data(edit_option=field)
        if field == 'performers':
            await message.answer('''При обновлении участников проекта старые участники сбрасываются
Введите новых участников''', reply_markup=staff_kb)
        else:
            await message.answer('Введите новое значение')
        await EditProject.EDITING_FIELD.set()
    elif option == 'Отменить':
        await message.answer_sticker('CAACAgIAAxkBAAEDZuVlx6DBQry15wn4Z03CwXTln4sWewAC2A8AAkjyYEsV-8TaeHRrmDQE', reply_markup=kb.main)
        await state.reset_state()
    else:
        await message.answer('Пожалуйста, выберите одну из предложенных опций редактирования')


@dp.message_handler(state=EditProject.EDITING_FIELD)
async def process_editing_field(message: types.Message, state: FSMContext):
     data = await state.get_data()
     edit_option = data.get('edit_option')

     if edit_option == 'performers':
         await process_editing_performers(message, state)
     elif edit_option == 'deadline':
         await process_editing_deadline(message, state)
     else:
         await process_editing_field_common(message, state)


async def process_editing_performers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    project_id = data.get('project_id')
    async with state.proxy() as data:
        if 'performers' not in data:
            data['performers'] = ''
        if message.text == 'Завершить':
            await message.answer('Обновление прошло успешно', reply_markup=kb.project_manager)
            await db.update_project_field(project_id, 'performers', data['performers'])
            await state.finish()
            return

        if data['performers']:
            data['performers'] += ", "
        data['performers'] += message.text


async def process_editing_deadline(message: types.Message, state: FSMContext):
    data = await state.get_data()
    project_id = data.get('project_id')
    try:
        date_obj = datetime.strptime(message.text, '%Y-%m-%d')
        async with state.proxy() as data:
            data['deadline'] = date_obj

        await db.update_project_field(project_id, 'deadline', data['deadline'])
        await message.answer('Обновление прошло успешно', reply_markup=kb.project_manager)
        await state.finish()

    except ValueError:
        await message.answer('Вы ввели неправильный формат даты. Введите в формате ГГ-ММ-ДД')

async def process_editing_field_common(message: types.Message, state: FSMContext):
    new_value = message.text
    data = await state.get_data()
    project_id = data.get('project_id')
    edit_option = data.get('edit_option')

    await db.update_project_field(project_id, edit_option, new_value)
    await message.answer('Обновление прошло успешно', reply_markup=kb.project_manager)
    await state.finish()


@dp.message_handler(text='Удалить проект')
@admin_access
async def delete_project(message: types.Message):
    await message.answer('Введите ID проекта, который хотите удалить')
    await DeleteProj.GET_ID.set()

@dp.message_handler(state=DeleteProj.GET_ID)
async def deleting_project(message: types.Message, state: FSMContext):
    project_id = message.text
    if await db.check_project_exists(project_id):
        await db.delete_project(project_id)
        await message.answer('Проект успешно удален', reply_markup=kb.project_manager)
    else:
        await message.answer('Проект с указанным ID не найден')
    await state.finish()


@dp.message_handler(text='Удалить сотрудника')
@admin_access
async def delete_staff(message: types.Message):
    await message.answer('Введите ID сотрудника, который хотите удалить')
    await DeleteStaff.GET_ID.set()


@dp.message_handler(state=DeleteStaff.GET_ID)
async def deleting_staff(message: types.Message, state: FSMContext):
    staff_id = message.text
    if await db.check_staff_exists(staff_id):
        await db.delete_staff(staff_id)
        await message.answer('Сотрудник успешно удален', reply_markup=kb.staff_manager)
    else:
        await message.answer('Сотрудник с указанным ID не найден')
    await state.finish()



@dp.message_handler(text='Главное меню')
@admin_access
async def back_to_main_menu(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAMpZBAAAfUO9xqQuhom1S8wBMW98ausAAI4CwACTuSZSzKxR9LZT4zQLwQ', reply_markup=kb.main)

@dp.message_handler(text='Назад')
@admin_access
async def back(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAEDauRlyLHsYLCYQP6qhXJWhUaBgMFFXAACDg0AAlkAAZhL3larpAvx_n80BA', reply_markup=kb.project_manager)

@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Я тебя не понимаю')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
