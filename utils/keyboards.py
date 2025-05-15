from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Поиск книги", callback_data="search_book")],
    [InlineKeyboardButton(text="Моя бронь", callback_data="user_booking")],
])

keyboard_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Искать по названию", callback_data="search_by_name"),],
    [InlineKeyboardButton(text="Искать по автору", callback_data="search_by_author"),],
    [InlineKeyboardButton(text="Искать по ISBN", callback_data="search_by_isbn"),],
    [InlineKeyboardButton(text="Искать по языку издания", callback_data="search_by_language"),],
    [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu")]
]) 

buttons_lang_arrows = [
    InlineKeyboardButton(text="⬅️", callback_data=f"languages_left"),
    InlineKeyboardButton(text="➡️", callback_data=f"languages_right")
]

keyboard_cancel_search = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [KeyboardButton(text="Отмена поиска")]
])

buttons_book_arrows = [
    InlineKeyboardButton(text="⬅️", callback_data=f"books_left"),
    InlineKeyboardButton(text="➡️", callback_data=f"books_right")
]

keyboard_send_contact = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="☎️ Отправить контакт", request_contact=True)]
])

keyboard_admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📙 Книги", callback_data="crud_books")],
    [InlineKeyboardButton(text="🖋 Авторы", callback_data="crud_authors")],
    [InlineKeyboardButton(text="👤 Пользователи", callback_data="crud_users")],
    [InlineKeyboardButton(text="📆 Брони", callback_data="crud_bookings")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")],
])

keyboard_admin_books = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить книгу", callback_data="add_book")],
    [InlineKeyboardButton(text="Найти книгу по ID", callback_data="find_book_id")],
    [InlineKeyboardButton(text="Найти книгу по ISBN", callback_data="find_book_isbn")],
    [InlineKeyboardButton(text="Найти книгу по названию", callback_data="find_book_title")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")]
])

keyboard_admin_authors = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text="Добавить автора", callback_data="add_author")],
    [InlineKeyboardButton(text="Найти автора по ID", callback_data="find_author_id")],
    [InlineKeyboardButton(text="Найти автора по имени", callback_data="find_author_name")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")]
])

keyboard_admin_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Найти пользователя по User ID", callback_data="find_user_id")],
    [InlineKeyboardButton(text="Найти пользователя по имени", callback_data="find_user_name")],
    [InlineKeyboardButton(text="Найти пользователя по телефону", callback_data="find_user_phone")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")]
])

keyboard_admin_bookings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Найти бронирование по ID", callback_data="find_booking_id")],
    [InlineKeyboardButton(text="Найти бронирование по номеру клиента", callback_data="find_booking_phone")],
    [InlineKeyboardButton(text="Найти бронирование по ISBN книги", callback_data="find_booking_isbn")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")]
])

keyboard_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_info")],
    [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_info")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")],
])

keyboard_edit_book = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить название", callback_data="edit_book_title")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")],
])

keyboard_edit_author = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить имя", callback_data="edit_author_name")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")],
])

keyboard_edit_user = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить имя", callback_data="edit_user_fullname")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")],
])

keyboard_edit_booking = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить статус", callback_data="edit_booking_status")],
    [InlineKeyboardButton(text="↩️ Вернуться в панель", callback_data="admin_panel")],
])