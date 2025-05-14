from aiogram import types, F, Router
from aiogram.filters.command import Command
from bot import ADMIN
from utils.keyboards import keyboard_admin_panel, keyboard_admin_books, keyboard_admin_authors, keyboard_admin_users, keyboard_admin_bookings, keyboard_edit, keyboard_edit_book, keyboard_edit_author, keyboard_edit_user, keyboard_edit_booking
import logging
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import create_book, get_books, get_author_info, get_user_info, get_booking_info, delete_record, edit_record
from datetime import datetime
from handlers.user import BOOK_PHOTO_ID
from database.models import BookingStatus

PANEL_PHOTO_ID = "AgACAgIAAxkBAAICgmgksbhPsOYcQM7hB4Zju6a_GeCrAAI1-TEbFKIoSUsGtUsUHt9hAQADAgADcwADNgQ"
AUTHOR_PHOTO_ID = "AgACAgIAAxkBAAIC5mgk_U_ZyBvSklcnvHHsvEa78ZU0AALt-zEbFKIoSbtXDjUq137fAQADAgADcwADNgQ"
USER_PHOTO_ID = "AgACAgIAAxkBAAIC6Ggk_V1v7iDXDHyC5pGXll8bdH4gAAL87DEbtckpSYshxpEDAjzTAQADAgADcwADNgQ"
BOOKING_PHOTO_ID = "AgACAgIAAxkBAAIC62gk_bkBCYmnjP8BNYTNAu6IaND-AALv-zEbFKIoSS4-_i23RyGyAQADAgADcwADNgQ"

admin_router = Router()

class AddBookStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_isbn = State()
    waiting_for_isbn13 = State()
    waiting_for_language = State()
    waiting_for_num_pages = State()
    waiting_for_publication_date = State()
    waiting_for_publisher = State()
    waiting_for_count_in_fund = State()
    waiting_for_age_limit = State()

class EditBookStates(StatesGroup):
    waiting_for_search_request = State()
    waiting_for_edit_message = State()

@admin_router.message(Command("admin"), F.from_user.id == ADMIN)
async def cmd_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer_photo(photo=PANEL_PHOTO_ID, caption="<b>Админ-панель</b>\n\nВыберите с чем будете работать", reply_markup=keyboard_admin_panel)


@admin_router.callback_query(F.data.startswith("crud"))
async def edit_keyboard(call: types.CallbackQuery):
    table = call.data.split("_")[-1]
    if table == "books":
        await call.message.edit_reply_markup(reply_markup=keyboard_admin_books)
    elif table == "authors":
        await call.message.edit_reply_markup(reply_markup=keyboard_admin_authors)
    elif table == "users":
        await call.message.edit_reply_markup(reply_markup=keyboard_admin_users)
    elif table == "bookings":
        await call.message.edit_reply_markup(reply_markup=keyboard_admin_bookings)


@admin_router.callback_query(F.data == "admin_panel")
async def admin_panel(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer_photo(photo=PANEL_PHOTO_ID, caption="<b>Админ-панель</b>\n\nВыберите с чем будете работать", reply_markup=keyboard_admin_panel)


@admin_router.callback_query(F.data == "add_book")
async def add_book(call: types.CallbackQuery, state: FSMContext):
    """Запрос названия книги"""
    await call.message.answer("Введите название книги")
    await state.set_state(AddBookStates.waiting_for_title)


@admin_router.message(AddBookStates.waiting_for_title)
async def get_title(message: types.Message, state: FSMContext):
    """Получение названия книги и запрос автора"""
    await state.update_data(title=message.text)
    await message.answer("Введите автора книги через запятую\n\nПример:\n<blockquote>J.K. Rowling,Mary GrandPré</blockquote>")
    await state.set_state(AddBookStates.waiting_for_author)


@admin_router.message(AddBookStates.waiting_for_author)
async def get_author(message: types.Message, state: FSMContext):
    """Получение автора книги и запрос ISBN-10"""
    authors = []
    for author in message.text.split(","):
        if author != "":
            authors.append(author.strip())

    await state.update_data(authors=authors)
    await message.answer("Введите ISBN книги в формате 10 цифр\n\nПример:\n<blockquote>0439785960</blockquote>")
    await state.set_state(AddBookStates.waiting_for_isbn)


@admin_router.message(AddBookStates.waiting_for_isbn)
async def get_isbn(message: types.Message, state: FSMContext):
    """Получение ISBN-10 книги и запрос ISBN-13"""
    is_valid = True
    if len(message.text) != 10:
        is_valid = False
    else:
        for symbol in message.text:
            if not symbol.isdigit() or symbol == "X":
                is_valid = False
                break
    if is_valid:
        await state.update_data(isbn=message.text)
        await message.answer("Введите ISBN книги в формате 13 цифр\n\nПример:\n<blockquote>9780679767473</blockquote>")
        await state.set_state(AddBookStates.waiting_for_isbn13)
    else:
        await message.answer("ISBN-10 введен некорректно")


@admin_router.message(AddBookStates.waiting_for_isbn13)
async def get_isbn13(message: types.Message, state: FSMContext):
    """Получение ISBN-13 книги и языка издания"""
    is_valid = True
    if len(message.text) != 13:
        is_valid = False
    else:
        for symbol in message.text:
            if not symbol.isdigit():
                is_valid = False
                break
    if is_valid:
        await state.update_data(isbn13=message.text)
        await message.answer("Введите язык издания книги\n\nПример:\n<blockquote>Английский (США)</blockquote>")
        await state.set_state(AddBookStates.waiting_for_language)
    else:
        await message.answer("ISBN-13 введен некорректно")


@admin_router.message(AddBookStates.waiting_for_language)
async def get_language(message: types.Message, state: FSMContext):
    """Получение языка издания и запрос количества страниц"""
    await state.update_data(language=message.text)
    await message.answer("Введите количество страниц книги")
    await state.set_state(AddBookStates.waiting_for_num_pages)


@admin_router.message(AddBookStates.waiting_for_num_pages)
async def get_num_pages(message: types.Message, state: FSMContext):
    """Получение количества страниц и запрос даты публикации"""
    number = int(message.text)
    if number > 0:
        await state.update_data(num_pages=number)
        await message.answer("Введите дату публикации книги в формате ДД.ММ.ГГГГ\n\nПример:\n<blockquote>16.09.2006</blockquote>")
        await state.set_state(AddBookStates.waiting_for_publication_date)
    else:
        await message.answer("Количество страниц должно быть больше 0")


@admin_router.message(AddBookStates.waiting_for_publication_date)
async def get_publication_date(message: types.Message, state: FSMContext):
    """Получение даты публикации и запрос издательства"""
    date = message.text.split(".")
    if len(date) == 3:
        day = int(date[0])
        month = int(date[1])
        if day > 0 and day < 32 and month > 0 and month < 13:
            date = datetime.strptime(message.text, "%d.%m.%Y")
            await state.update_data(publication_date=date)
            await message.answer("Введите издательство книги")
            await state.set_state(AddBookStates.waiting_for_publisher)
        else:
            await message.answer("Дата публикации введена некорректно")
    else:
        await message.answer("Дата публикации введена некорректно")


@admin_router.message(AddBookStates.waiting_for_publisher)
async def get_publisher(message: types.Message, state: FSMContext):
    """Получение издательства и запрос количества в наличии"""
    await state.update_data(publisher=message.text)
    await message.answer("Введите количество книг в наличии")
    await state.set_state(AddBookStates.waiting_for_count_in_fund)


@admin_router.message(AddBookStates.waiting_for_count_in_fund)
async def get_count_in_fund(message: types.Message, state: FSMContext):
    """Получение количества в наличии и запрос возрастного ограничения"""
    if message.text.isdigit():
        count = int(message.text)
        if count > 0:
            await state.update_data(count_in_fund=count)
            await message.answer("Введите возрастное ограничение книги")
            await state.set_state(AddBookStates.waiting_for_age_limit)
        else:
            await message.answer("Количество книг в наличии должно быть больше 0")
    else:
        await message.answer("Количество книг в наличии должно быть числом")


@admin_router.message(AddBookStates.waiting_for_age_limit)
async def get_age_limit(message: types.Message, state: FSMContext):
    """Получение возрастного ограничения и добавление книги"""
    data = await state.get_data()
    if message.text.isdigit():
        age_limit = int(message.text)
        if age_limit >= 0:
            try:
                create_book(title=data.get("title"),
                            isbn=data.get("isbn"),
                            isbn13=data.get("isbn"),
                            num_pages=data.get("num_pages"),
                            publisher=data.get("publisher"),
                            publication_date=data.get("publication_date"),
                            age_limit=age_limit,
                            count_in_fund=data.get("count_in_fund"),
                            author_names=data.get("authors"),
                            language=data.get("language"),
                            )
                await message.answer("Книга успешно добавлена")

            except ValueError as e:
                await message.answer(f"{str(e)}")

            await state.clear()
        else:
            await message.answer("Возрастное ограничение должно быть больше или равно 0")
    else:
        await message.answer("Возрастное ограничение должно быть числом")


@admin_router.callback_query(F.data.startswith("find"))
async def find_book(call: types.CallbackQuery, state: FSMContext):
    """Запрос информации о интересующей записи"""
    model = call.data.split("_")[1]
    column = call.data.split("_")[-1]
    await state.update_data(model=model, column=column)
    if model == "book":
        if column == "id":
            await call.message.answer("Введите ID книги")
        elif column == "title":
            await call.message.answer("Введите название книги")
        elif column == "isbn":
            await call.message.answer("Введите ISBN книги")
    elif model == "author":
        if column == "id":
            await call.message.answer("Введите ID автора")
        elif column == "name":
            await call.message.answer("Введите имя автора")
    elif model == "user":
        if column == "id":
            await call.message.answer("Введите ID пользователя")
        elif column == "name":
            await call.message.answer("Введите имя пользователя")
        elif column == "phone":
            await call.message.answer("Введите номер телефона пользователя")
    elif model == "booking":
        if column == "id":
            await call.message.answer("Введите ID бронирования")
        elif column == "phone":
            await call.message.answer("Введите номер телефона клиента")
        elif column == "isbn":
            await call.message.answer("Введите ISBN бронируемой книги")
    await state.set_state(EditBookStates.waiting_for_search_request)


@admin_router.message(EditBookStates.waiting_for_search_request)
async def search_record(message: types.Message, state: FSMContext):
    """Обработка запроса и вывод результата"""
    request = message.text
    data = await state.get_data()
    model = data.get("model")
    column = data.get("column")
    try:
        if model == "book":
            books = None
            error = None

            if column == "id":
                if request.isdigit():
                    books = get_books(id=int(request))
                else:
                    error = "ID книги введено некорректно"
            elif column == "title":
                books = get_books(title=request)
            elif column == "isbn":
                is_valid = True
                if len(request) != 10 and len(request) != 13:
                    is_valid = False
                else:
                    for symbol in request:
                        if not symbol.isdigit() or symbol == "X":
                            is_valid = False
                            break
                
                if is_valid:
                    books = get_books(isbn=request)
                else:
                    error = "ISBN введен некорректно"

            if error:
                await message.answer(error)
            elif books:
                book = books[0]
                await state.update_data(book=book)

                authors = ", ".join([author.name for author in book.authors]) if len(book.authors) > 1 else book.authors[0].name

                await message.answer_photo(photo=BOOK_PHOTO_ID,
                                    caption=f"<b>🔐 ID:</b> <code>{book.id}</code>\n\n"
                                    f"<b>📖 Название:</b> <code>{book.title}</code>\n"
                                    f"<b>👥 Авторы:</b> <code>{authors}</code>\n"
                                    f"<b>🌐 Язык издания:</b> <code>{book.language}</code>\n"
                                    f"<b>📌 ISBN(10/13):</b> <code>{book.isbn}</code> / <code>{book.isbn13}</code>\n"
                                    f"<b>📝 Количество страниц:</b> <code>{book.num_pages}</code>\n"
                                    f"<b>⭐ Рейтинг:</b> <code>{book.average_rating}</code>\n"
                                    f"<b>📅 Дата публикации:</b> <code>{book.publication_date}</code>\n"
                                    f"<b>🖨️ Издательство:</b> <code>{book.publisher}</code>\n"
                                    f"<b>🧮 Количество в наличии:</b> <code>{book.count_in_fund}</code>\n",
                                    reply_markup=keyboard_edit,
                                    )
            else:
                await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")

        elif model == "author":
            author = None
            error = None

            if column == "id":
                if request.isdigit():
                    author = get_author_info(id=int(request))
                else:
                    error = "ID автора введено некорректно"
            elif column == "name":
                author = get_author_info(name=request)

            if error:
                await message.answer(error)
            elif author:
                await state.update_data(author=author)

                await message.answer_photo(photo=AUTHOR_PHOTO_ID,
                                    caption=f"<b>🔐 ID:</b> <code>{author.id}</code>\n\n"
                                    f"<b>👤 Имя:</b> <code>{author.name}</code>\n",
                                    reply_markup=keyboard_edit,
                                    )
            else:
                await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")

        elif model == "user":
            user = None
            error = None

            if column == "id":
                if request.isdigit():
                    user = get_user_info(user_id=int(request))
                else:
                    error = "ID пользователя введено некорректно"
            elif column == "name":
                user = get_user_info(name=request)
            elif column == "phone":
                if request.isdigit() and len(request) == 11:
                    user = get_user_info(phone=int(request))
                else:
                    error = "Номер телефона пользователя введен некорректно"

            if error:
                await message.answer(error)
            elif user:
                await state.update_data(user=user)

                await message.answer_photo(photo=USER_PHOTO_ID,
                                    caption=f"<b>🔐 ID:</b> <code>{user.user_id}</code>\n\n"
                                    f"<b>👤 Имя:</b> <code>{user.fullname}</code>\n"
                                    f"<b>📅 Возраст:</b> <code>{user.age}</code>\n"
                                    f"<b>📞 Телефон:</b> <code>{user.phone_number}</code>\n",
                                    reply_markup=keyboard_edit,
                                    )
            else:
                await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")

        elif model == "booking":
            booking = None
            error = None

            if column == "id":
                if request.isdigit():
                    booking = get_booking_info(id=int(request))
                else:
                    error = "ID пользователя введено некорректно"

            elif column == "isbn":
                is_valid = True
                if len(request) != 10 and len(request) != 13:
                    is_valid = False
                else:
                    for symbol in request:
                        if not symbol.isdigit() or symbol == "X":
                            is_valid = False
                            break
                
                if is_valid:
                    booking = get_booking_info(isbn=request)
                else:
                    error = "ISBN введен некорректно"

            elif column == "phone":
                if request.isdigit() and len(request) == 11:
                    booking = get_booking_info(phone=int(request))
                else:
                    error = "Номер телефона пользователя введен некорректно"

            if error:
                await message.answer(error)
            elif booking:
                await state.update_data(booking=booking)

                await message.answer_photo(photo=BOOKING_PHOTO_ID,
                                    caption=f"<b>🔐 ID:</b> <code>{booking.id}</code>\n\n"
                                    f"<b>📘 Книга:</b> <code>{booking.book.title}</code>\n"
                                    f"<b>👤 Пользователь:</b> <code>{booking.user.fullname}</code>\n"
                                    f"<b>📅 Дата брони:</b> <code>{booking.booking_date}</code>\n"
                                    f"<b>📅 Дата окончания брони:</b> <code>{booking.booking_deadline}</code>\n"
                                    f"<b>🟢 Статус брони:</b> <code>{booking.status.value}</code>\n",
                                    reply_markup=keyboard_edit,
                                    )
            else:
                await message.answer("😔 <b>Ничего не нашел по вашему запросу</b>")

    except ValueError as e:
        await message.answer(f"{str(e)}")


@admin_router.callback_query(F.data == "delete_info")
async def delete_info(call: types.CallbackQuery, state: FSMContext):
    """Удаление записи"""
    data = await state.get_data()

    try:
        if data.get("book"):
            delete_record(book=data.get("book"))
        elif data.get("author"):
            delete_record(author=data.get("author"))
        elif data.get("user"):
            delete_record(user=data.get("user"))
        elif data.get("booking"):
            delete_record(booking=data.get("booking"))
        await call.message.answer("Запись успешно удалена")
        await state.clear()
    except ValueError as e:
        await call.message.answer(f"{str(e)}")


@admin_router.callback_query(F.data == "edit_info")
async def keyboard_for_edit(call: types.CallbackQuery, state: FSMContext):
    """Изменяем клавиатуру взависимости от того, какую таблицу изменяем"""
    data = await state.get_data()

    if data.get("book"):
        await call.message.edit_reply_markup(reply_markup=keyboard_edit_book)
    elif data.get("author"):
        await call.message.edit_reply_markup(reply_markup=keyboard_edit_author)
    elif data.get("user"):
        await call.message.edit_reply_markup(reply_markup=keyboard_edit_user)
    elif data.get("booking"):
        await call.message.edit_reply_markup(reply_markup=keyboard_edit_booking)


@admin_router.callback_query(F.data.startswith("edit"))
async def edit_info(call: types.CallbackQuery, state: FSMContext):
    """Запрос нового значения"""
    column = call.data.split("_")[-1]
    await state.update_data(column=column)
    await state.set_state(EditBookStates.waiting_for_edit_message)
    if column == "status":
        await call.message.answer("Введите новое значение")
    else:
        await call.message.answer("Введите новое значение")


@admin_router.message(EditBookStates.waiting_for_edit_message)
async def edit_message(message: types.Message, state: FSMContext):
    """Изменение значения записи"""
    data = await state.get_data()
    model = data.get("model")
    column = data.get("column")

    try:
        if model == "book":
            if column == "title":
                edit_record(book=data.get("book"), column=column, value=message.text)
        elif model == "author":
            if column == "name":
                edit_record(author=data.get("author"), column=column, value=message.text)
        elif model == "user":
            if column == "fullname":
                edit_record(user=data.get("user"), column=column, value=message.text)
        elif model == "booking":
            if column == "status":
                found_status = None
                for status in BookingStatus:
                    if status.value.lower() == message.text.lower():
                        found_status = status
                        break

                if found_status:
                    edit_record(booking=data.get("booking"), column=column, value=message.text)
                else:
                    await message.answer("Статус бронирования введен некорректно")
        await message.answer("Запись успешно изменена")
        await state.clear()
    except ValueError as e:
        await message.answer(f"{str(e)}")


# @admin_router.message()
# async def ignore_messages(message: types.Message):
#     await message.answer(message.photo[0].file_id)
