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