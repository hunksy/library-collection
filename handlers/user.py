from aiogram import types, Router, F
from aiogram.filters.command import Command
import logging
from utils.keyboards import keyboard_menu, keyboard_search, buttons_lang_arrows, keyboard_cancel_search, buttons_book_arrows, keyboard_send_contact
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import get_books, get_languages, get_count_of_languages, register_user, last_booking, has_registration, reserve_book, cancel_current_booking
from database.models import BookingStatus

MENU_PHOTO_ID = "AgACAgIAAxkBAAIBX2gjNZvsw4OBVodhbiZkgJsI7bE2AAJl9TEb6pwZSYp6A4dviAuOAQADAgADcwADNgQ"
BOOK_PHOTO_ID = "AgACAgIAAxkBAAPyaCJrt5YFCWN4BG9gGuJbOGCFNHcAAon3MRvqnBFJ7ZLyAf13JFcBAAMCAANzAAM2BA"

user_router = Router()

class States(StatesGroup):
    waiting_for_search_request = State()
    waiting_for_fullname = State()
    waiting_for_age = State()
    waiting_for_phone_number = State()

@user_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Регистрация пользователей"""
    logging.info(f"Пользователь {message.from_user.id} начал регистрацию")

    if has_registration(message.from_user.id):
        await message.answer(f"Привет, {message.from_user.full_name}! Вы успешно прошли регистрацию и можете пользоваться ботом!")
    else:
        await message.answer(f"Привет, {message.from_user.full_name}! Перед использованием бота необходимо пройти регистрацию")
        await message.answer("Введите ваше ФИО")
        await state.set_state(States.waiting_for_fullname)


@user_router.message(States.waiting_for_fullname)
async def get_fullname(message: types.Message, state: FSMContext):
    """Получение ФИО и запрос возраста"""

    fullname = message.text
    if len(fullname.split(" ")) == 3:
        await state.update_data(fullname=message.text)

        await message.answer("Введите ваш полный возраст")
        await state.set_state(States.waiting_for_age)
    else:
        await message.answer("ФИО введено некорректно")


@user_router.message(States.waiting_for_age)
async def get_age(message: types.Message, state: FSMContext):
    """Получение возраста и запрос номера"""

    age = message.text
    if age.isdigit():
        await state.update_data(age=int(message.text))

        await message.answer("Введите ваш номер телефона или нажмите кнопку отправить контакт", reply_markup=keyboard_send_contact)
        await state.set_state(States.waiting_for_phone_number)
    else:
        await message.answer("Возраст введен некорректно")


@user_router.message(States.waiting_for_phone_number)
async def get_age(message: types.Message, state: FSMContext):
    """Получение номера и регистрация"""

    phone_number = ""
    if message.contact:
        if message.contact.user_id == message.from_user.id:
            phone_number = message.contact.phone_number
            phone_number = phone_number.replace("+", "")
        else:
            await message.answer("Это не ваш контакт, попробуйте снова")
    else:
        for symbol in message.text:
            if symbol.isdigit():
                phone_number += symbol

    if phone_number != None and len(phone_number) == 11:
        data = await state.get_data()
        fullname = data.get("fullname")
        age = data.get("age")
        phone_number = int(phone_number)
        try:
            await state.clear()
            register_user(user_id=message.from_user.id, fullname=fullname, age=age, phone_number=phone_number)
            await message.answer(f"Регистрация прошла успешно теперь вам доступна команда /menu", reply_markup=types.ReplyKeyboardRemove())
        except ValueError:
            await message.answer("Возникла ошибка при регистрации")
    else:
        await message.answer("Номер телефона введен некорректно")


@user_router.message(Command("id"))
async def cmd_id(message: types.Message):
    """Команда для получения id, чтобы определеить админа в .env"""

    logging.info(f"Пользователь {message.from_user.id} использовал команду /id")

    await message.answer(f"Ваш id: {message.from_user.id}")


async def show_menu(message: types.Message):
    """Фукнция для отправки меню."""

    if has_registration(message.from_user.id):
        await message.answer_photo(photo=MENU_PHOTO_ID, caption="<b>Главное меню:</b>", reply_markup=keyboard_menu)
    else:
        await message.answer("Сначала пройдите регистрацию через команду /start")
    logging.info(f"Пользователь {message.from_user.id} запросил меню")


@user_router.message(Command("menu"))
async def cmd_menu(message: types.Message): 
    """Команда для отправки меню"""

    await show_menu(message)


async def cancel_search(message: types.Message, state: FSMContext):
    """Функция отмены поиска"""

    await message.delete()
    await state.clear()
    await show_menu(message)

@user_router.message(F.text.lower().contains("отмена"))
async def cancel_reply(message: types.Message, state: FSMContext):
    """Отмена через Reply-кнопку"""

    await cancel_search(message, state)


@user_router.callback_query(F.data == "cancel_search")
async def cancel_search_inline(call: types.CallbackQuery, state: FSMContext):
    """Отмена поиска через Inline-кнопку"""

    await cancel_search(call.message, state)


@user_router.callback_query(F.data == "search_book")
async def search_book(call: types.CallbackQuery, state: FSMContext):
    """Поиск книги"""

    logging.info(f"Пользователь {call.from_user.id} начал поиск книги")

    await state.update_data(language_index = 0)
    await call.message.edit_reply_markup(reply_markup=keyboard_search)


@user_router.callback_query(F.data == "search_by_name")
async def search_by_name(call: types.CallbackQuery, state: FSMContext):
    """Поиск по названию"""
    
    await state.set_state(States.waiting_for_search_request)
    await state.update_data(is_search_by_name=True)
    await call.message.answer("Введите название книги", reply_markup=keyboard_cancel_search)


@user_router.callback_query(F.data == "search_by_author")
async def search_by_author(call: types.CallbackQuery, state: FSMContext):
    """Поиск по автору"""
    
    await state.set_state(States.waiting_for_search_request)
    await state.update_data(is_search_by_author=True)
    await call.message.answer("Введите интересующего вас автора", reply_markup=keyboard_cancel_search)


@user_router.callback_query(F.data == "search_by_isbn")
async def search_by_isbn(call: types.CallbackQuery, state: FSMContext):
    """Поиск по ISBN"""
    
    await state.set_state(States.waiting_for_search_request)
    await state.update_data(is_search_by_isbn=True)
    await call.message.answer("Введите ISBN книги (из 10 или 13 цифр)", reply_markup=keyboard_cancel_search)


async def generate_keyboard_langs(message: types.Message, index: int):
    """Генерация клавиатуры для выбора языка"""

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
    try:
        languages = get_languages(index)
        for language in languages:
            button_language = [types.InlineKeyboardButton(text=language[0], callback_data=f"language_{language[0]}")]
            keyboard.inline_keyboard.insert(0, button_language)
    except ValueError:
        await message.answer("Возникла ошибка при получении языков")

    keyboard.inline_keyboard.append(buttons_lang_arrows)
    cancel_button = types.InlineKeyboardButton(text="Отмена поиска", callback_data="cancel_search")
    keyboard.inline_keyboard.append([cancel_button])
    
    return keyboard


@user_router.callback_query(F.data == "search_by_language")
async def search_by_language(call: types.CallbackQuery, state: FSMContext):
    """Выбор языка издания"""

    await call.message.edit_caption(caption="<b>Выберите язык издания: </b>")

    data = await state.get_data()
    index = data.get("language_index")

    keyboard = await generate_keyboard_langs(call.message, index)

    await state.update_data(language_index=index)
    await call.message.edit_reply_markup(reply_markup=keyboard)


@user_router.callback_query(F.data.startswith("languages"))
async def language_arrows(call: types.CallbackQuery, state: FSMContext):
    """Перемещение между языками издания"""

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
        keyboard = await generate_keyboard_langs(call.message, index)

        await state.update_data(language_index=index)
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        pass


async def generate_keyboard_books(book):
    keyboard_book = types.InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_book.inline_keyboard.append(buttons_book_arrows)
    booking_button = []
    if book.is_available():
        booking_button.append(types.InlineKeyboardButton(text="✅ Забронировать", callback_data=f"booking_{book.id}"))
    else:
        booking_button.append(types.InlineKeyboardButton(text="❌ Нет в наличии"))
    keyboard_book.inline_keyboard.append(booking_button)
    return keyboard_book


async def show_book(message: types.Message, book):
    """Функция для отображения информации о книге"""

    if book != None:
        authors = ", ".join([author.name for author in book.authors]) if len(book.authors) > 1 else book.authors[0].name

        keyboard = await generate_keyboard_books(book)

        await message.answer("<b>🔎 Вот что я нашел:</b>")
        await message.answer_photo(photo=BOOK_PHOTO_ID,
                            caption=f"<b>📖 Название:</b> {book.title}\n"
                            f"<b>👥 Авторы:</b> {authors}\n"
                            f"<b>🌐 Язык издания:</b> {book.language}\n"
                            f"<b>📌 ISBN(10/13):</b> <code>{book.isbn}</code> / <code>{book.isbn13}</code>\n"
                            f"<b>📝 Количество страниц:</b> {book.num_pages}\n"
                            f"<b>⭐ Рейтинг:</b> {book.average_rating}\n"
                            f"<b>📅 Дата публикации:</b> {book.publication_date}\n"
                            f"<b>🖨️ Издательство:</b> {book.publisher}\n",
                            reply_markup=keyboard,
                            )
    else:
        await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")


@user_router.callback_query(F.data.startswith("language"))
async def search_language(call: types.CallbackQuery, state: FSMContext):
    """Поиск по языку издания"""

    books = None
    language = call.data.split("_")[-1]

    try:
        books = get_books(language=language)
    except ValueError:
        call.message.answer("Возникла ошибка при поиске книги")

    logging.info(f"Пользователь {call.from_user.id} получил результаты поиска по запросу {language}")
    
    if len(books) != 0:
        index = 0
        await state.update_data(book_index=index, books=books)
        await show_book(call.message, books[0])
    else:
        await call.message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")


@user_router.message(States.waiting_for_search_request)
async def search_by_request(message: types.Message, state: FSMContext):
    """Поиск по введенным данным"""

    data = await state.get_data()
    books = None

    try:
        if data.get("is_search_by_name"):
            books = get_books(title=message.text)
        elif data.get("is_search_by_author"):
            books = get_books(author=message.text)
        elif data.get("is_search_by_isbn"):
            isbn = message.text
            if(len(isbn) != 10 and len(isbn) != 13):
                await message.answer("ISBN должен состоять из 10 или 13 цифр")
            else:
                books = get_books(isbn=isbn)
        
    except ValueError:
        message.answer("Возникла ошибка при поиске книги")

    logging.info(f"Пользователь {message.from_user.id} получил результаты поиска по запросу {message.text}")

    if len(books) != 0:
        index = 0
        await state.update_data(book_index=index, books=books)
        await show_book(message, books[0])
    else:
        await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")


@user_router.callback_query(F.data.startswith("books"))
async def book_arrows(call: types.CallbackQuery, state: FSMContext):
    """Перемещение между найденными книгами"""

    direction = call.data.split("_")[-1]
    data = await state.get_data()
    books = data.get("books")
    index = data.get("book_index")
    maximum = len(books)

    if(direction == "left"):
        if(index > 0):
            index -= 1
    else:
        if(index < maximum - 1):
            index += 1
    
    book = books[index]
    if book != None:
        await state.update_data(book_index=index)

        authors = ", ".join([author.name for author in book.authors]) if len(book.authors) > 1 else book.authors[0].name

        keyboard = await generate_keyboard_books(book)

        await call.message.edit_caption(caption=f"<b>📖 Название:</b> {book.title}\n"
                            f"<b>👥 Авторы:</b> {authors}\n"
                            f"<b>🌐 Язык издания:</b> {book.language}\n"
                            f"<b>📌 ISBN(10/13):</b> <code>{book.isbn}</code> / <code>{book.isbn13}</code>\n"
                            f"<b>📝 Количество страниц:</b> {book.num_pages}\n"
                            f"<b>⭐ Рейтинг:</b> {book.average_rating}\n"
                            f"<b>📅 Дата публикации:</b> {book.publication_date}\n"
                            f"<b>🖨️ Издательство:</b> {book.publisher}\n"
                            f"\n🔢 {index+1} из {maximum}",
                            reply_markup=keyboard,
                            )


@user_router.callback_query(F.data.startswith("booking"))
async def reserve_a_book(call: types.CallbackQuery):
    booking = last_booking(call.from_user.id)
    if booking != None and booking.status == BookingStatus.RESERVED:
        await call.answer("У вас уже есть бронь книги!", show_alert=True)
    else:
        book_id = int(call.data.split("_")[-1])
        new_booking = reserve_book(book_id=book_id, user_id=call.from_user.id)
        deadline = new_booking.booking_deadline
        deadline = f"{deadline.day}.{deadline.month}.{deadline.year} {deadline.hour}:{deadline.minute}"
        await call.message.answer(f"Книга успешно забронирована!\n"
                                f"Получите её до {deadline} в библиотеке")


@user_router.callback_query(F.data == "user_booking")
async def show_user_booking(call: types.callback_query):
    booking = last_booking(call.from_user.id)
    if booking != None and booking.status == BookingStatus.RESERVED:
        book = booking.book
        deadline = booking.booking_deadline
        deadline = f"{deadline.day}.{deadline.month}.{deadline.year} {deadline.hour}:{deadline.minute}"

        if book != None:
            authors = ", ".join([author.name for author in book.authors]) if len(book.authors) > 1 else book.authors[0].name
            
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
            cancel_booking = [types.InlineKeyboardButton(text="❌ Отменить бронь", callback_data=f"cancel_booking")]
            keyboard.inline_keyboard.append(cancel_booking)

            await call.message.answer_photo(photo=BOOK_PHOTO_ID,
                                    caption=f"<b><i>✅ Ваша бронь:</i></b>\n\n"
                                    f"<b>📖 Название:</b> {book.title}\n"
                                    f"<b>👥 Авторы:</b> {authors}\n"
                                    f"<b>🌐 Язык издания:</b> {book.language}\n"
                                    f"<b>📌 ISBN(10/13):</b> <code>{book.isbn}</code> / <code>{book.isbn13}</code>\n"
                                    f"<b>📝 Количество страниц:</b> {book.num_pages}\n"
                                    f"<b>⭐ Рейтинг:</b> {book.average_rating}\n"
                                    f"<b>📅 Дата публикации:</b> {book.publication_date}\n"
                                    f"<b>🖨️ Издательство:</b> {book.publisher}\n"
                                    f"\n⏳ Получите до: {deadline}",
                                    reply_markup=keyboard,
                                    )
    else:
        await call.answer("У вас нет действующей брони!", show_alert=True)


@user_router.callback_query(F.data == "cancel_booking")
async def cancel_booking(call: types.callback_query):
    current_booking = last_booking(call.from_user.id)
    if current_booking != None and current_booking.status == BookingStatus.RESERVED:
        cancel_current_booking(current_booking)
        await call.answer("Бронь книги успешна отменена!", show_alert=True)
        await call.message.delete()
    else:
        await call.answer("У вас нет действующей брони!", show_alert=True)


@user_router.message()
async def ignore_messages(message: types.Message):
    """Игнорирование всех сообщений кроме команд"""

    await message.answer("Используйте команду /menu для взаимодействия с ботом")

    # if message.photo:
    #     await message.answer(message.photo[0].file_id)
