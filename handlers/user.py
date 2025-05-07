from aiogram import types, Router, F
from aiogram.filters.command import Command
import logging
from utils.keyboards import kb_menu, kb_search, arrows
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import get_book, get_languages, get_count_of_languages

user_router = Router()

class States(StatesGroup):
    waiting_for_search_request = State()


@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} использовал команду /start")

    await message.answer(f"Привет, {message.from_user.full_name}!")


@user_router.message(Command("id"))
async def cmd_id(message: types.Message):
    """Команда для получения id, чтобы определеить админа в .env"""

    logging.info(f"Пользователь {message.from_user.id} использовал команду /id")

    await message.answer(f"Ваш id: {message.from_user.id}")


@user_router.message(Command("menu"))
async def cmd_menu(message: types.Message): 
    """Команда для отправки меню"""

    logging.info(f"Пользователь {message.from_user.id} использовал команду /menu")

    await message.answer("<b>МЕНЮ:</b>", reply_markup=kb_menu)


@user_router.callback_query(F.data == "search_book")
async def search_book(call: types.CallbackQuery, state: FSMContext):
    """Поиск книги"""

    logging.info(f"Пользователь {call.message.from_user.id} начал поиск книги")

    await state.update_data(language_index = 0)
    await call.message.edit_reply_markup(reply_markup=kb_search)


@user_router.callback_query(F.data == "search_by_name")
async def search_by_name(call: types.CallbackQuery, state: FSMContext):
    """Поиск по названию"""
    
    await state.set_state(States.waiting_for_search_request)
    await state.update_data(is_search_by_name=True)
    await call.message.answer("Введите название книги")


@user_router.callback_query(F.data == "search_by_author")
async def search_by_author(call: types.CallbackQuery, state: FSMContext):
    """Поиск по автору"""
    
    await state.set_state(States.waiting_for_search_request)
    await state.update_data(is_search_by_author=True)
    await call.message.answer("Введите интересующего вас автора")


@user_router.callback_query(F.data == "search_by_isbn")
async def search_by_isbn(call: types.CallbackQuery, state: FSMContext):
    """Поиск по ISBN"""
    
    await state.set_state(States.waiting_for_search_request)
    await state.update_data(is_search_by_isbn=True)
    await call.message.answer("Введите ISBN книги (из 10 или 13 цифр)")


@user_router.callback_query(F.data == "search_by_language")
async def search_by_language(call: types.CallbackQuery, state: FSMContext):
    """Выбор языка издания"""

    await call.message.edit_text("<b>Выберите язык издания: </b>")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
    data = await state.get_data()
    index = data.get("language_index")

    try:
        languages = get_languages(index)
        for language in languages:
            button_language = [types.InlineKeyboardButton(text=language[0], callback_data=f"language_{language[0]}")]
            keyboard.inline_keyboard.insert(0, button_language)
    except ValueError as e:
        logging.error(f"Ошибка при получении языков: {str(e)}")
        await call.message.answer("Возникла ошибка при получении языков")

    keyboard.inline_keyboard.append(arrows)

    await call.message.edit_reply_markup(reply_markup=keyboard)


@user_router.callback_query(F.data.startswith("languages"))
async def language_arrows(call: types.CallbackQuery, state: FSMContext):
    direction = call.data.split("_")[-1]
    maximum = get_count_of_languages()
    data = await state.get_data()
    index = data.get("language_index")
    is_changed = False

    if(direction == "left"):
        if(index > 0):
            index -= 5
            is_changed = True
    else:
        if(index < maximum - 5):
            index += 5
            is_changed = True

    
    if is_changed:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])

        try:
            languages = get_languages(index)
            for language in languages:
                button_language = [types.InlineKeyboardButton(text=language[0], callback_data=f"language_{language[0]}")]
                keyboard.inline_keyboard.insert(0, button_language)
        except ValueError as e:
            logging.error(f"Ошибка при получении языков: {str(e)}")
            await call.message.answer("Возникла ошибка при получении языков")

        keyboard.inline_keyboard.append(arrows)

        await state.update_data(language_index=index)
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        pass


@user_router.callback_query(F.data.startswith("language"))
async def search_language(call: types.CallbackQuery):
    """Поиск по языку издания"""

    book = None
    language = call.data.split("_")[-1]
    print(language)
    try:
        book = get_book(language=language)
    except ValueError as e:
        logging.error(f"Ошибка при поиске книги: {str(e)}")
        call.message.answer("Возникла ошибка при поиске книги")

    logging.info(f"Пользователь {call.from_user.id} получил результаты поиска по запросу {language}")
    if book != None:
        authors = ", ".join([author.name for author in book.authors]) if len(book.authors) > 1 else book.authors[0].name

        await call.message.answer("<b>Вот что я нашел:</b>")
        await call.message.answer(f"<b>Название:</b> {book.title}\n<b>Авторы:</b> {authors}\n<b>Язык издания:</b> {book.language}\n")
    else:
        await call.message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")


@user_router.message(States.waiting_for_search_request)
async def search_by_request(message: types.Message, state: FSMContext):
    """Поиск по введенным данным"""

    data = await state.get_data()
    book = None

    try:
        if data.get("is_search_by_name"):
            book = get_book(title=message.text)
        elif data.get("is_search_by_author"):
            book = get_book(author=message.text)
        elif data.get("is_search_by_isbn"):
            isbn = message.text
            if(len(isbn) != 10 and len(isbn) != 13):
                await message.answer("ISBN должен состоять из 10 или 13 цифр")
            else:
                book = get_book(isbn=isbn)
        
    except ValueError as e:
        logging.error(f"Ошибка при поиске книги: {str(e)}")
        message.answer("Возникла ошибка при поиске книги")

    logging.info(f"Пользователь {message.from_user.id} получил результаты поиска по запросу {message.text}")
    if book != None:
        authors = ", ".join([author.name for author in book.authors]) if len(book.authors) > 1 else book.authors[0].name

        await message.answer("<b>Вот что я нашел:</b>")
        await message.answer(f"<b>Название:</b> {book.title}\n<b>Авторы:</b> {authors}\n<b>Язык издания:</b> {book.language}\n")
    else:
        await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")


@user_router.message()
async def ignore_messages(message: types.Message):
    """Игнорирование всех сообщений кроме команд"""

    await message.answer("Используйте команду /menu для взаимодействия с ботом")